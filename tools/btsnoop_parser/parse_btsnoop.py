#!/usr/bin/env python3
"""Minimal btsnoop + HCI + L2CAP parser for GKE printer capture analysis."""
import struct
import sys
from collections import defaultdict

BTSNOOP_EPOCH_OFFSET = 0x00E03AB44A676000  # not used precisely, just for relative ordering

def read_records(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"btsnoop\x00", "not a btsnoop file"
    version, datalink = struct.unpack(">II", data[8:16])
    print(f"btsnoop version={version} datalink={datalink}")
    off = 16
    records = []
    while off < len(data):
        if off + 24 > len(data):
            break
        orig_len, incl_len, flags, drops, ts = struct.unpack(">IIIIq", data[off:off+24])
        off += 24
        pkt = data[off:off+incl_len]
        off += incl_len
        records.append((ts, flags, pkt))
    return records

def hexdump(b, maxlen=64):
    b2 = b[:maxlen]
    h = " ".join(f"{x:02x}" for x in b2)
    if len(b) > maxlen:
        h += " ..."
    return h

def parse(path):
    records = read_records(path)
    print(f"total records: {len(records)}")

    # ACL reassembly buffers keyed by connection handle
    acl_buf = {}   # handle -> bytearray accumulating
    acl_want = {}  # handle -> expected total l2cap payload length (from first fragment's L2CAP length field + 4 header bytes)
    l2cap_channels = defaultdict(int)
    att_events = []
    other_l2cap_events = []
    events_seen = []
    commands_seen = []

    for idx, (ts, flags, pkt) in enumerate(records):
        if not pkt:
            continue
        direction = "host->ctrl" if not (flags & 0x01) else "ctrl->host"
        pkt_type = pkt[0]
        body = pkt[1:]

        if pkt_type == 0x01:  # HCI Command
            if len(body) >= 3:
                opcode = struct.unpack("<H", body[0:2])[0]
                commands_seen.append((idx, direction, opcode, hexdump(body)))
            continue

        if pkt_type == 0x04:  # HCI Event
            if len(body) >= 2:
                evt_code = body[0]
                events_seen.append((idx, direction, evt_code, hexdump(body)))
            continue

        if pkt_type == 0x02:  # HCI ACL Data
            if len(body) < 4:
                continue
            handle_flags, data_len = struct.unpack("<HH", body[0:4])
            handle = handle_flags & 0x0FFF
            pb = (handle_flags >> 12) & 0x3
            acl_payload = body[4:4+data_len]

            if pb == 0b10 or pb == 0b00:  # start fragment
                if len(acl_payload) < 4:
                    continue
                l2cap_len, cid = struct.unpack("<HH", acl_payload[0:4])
                sdu = acl_payload[4:]
                if len(sdu) >= l2cap_len:
                    # complete in one fragment
                    l2cap_channels[cid] += 1
                    handle_l2cap_payload(cid, sdu[:l2cap_len], idx, direction, ts, att_events, other_l2cap_events)
                else:
                    acl_buf[handle] = bytearray(sdu)
                    acl_want[handle] = (cid, l2cap_len)
            elif pb == 0b01:  # continuation
                if handle in acl_buf:
                    acl_buf[handle].extend(acl_payload)
                    cid, want = acl_want[handle]
                    if len(acl_buf[handle]) >= want:
                        l2cap_channels[cid] += 1
                        handle_l2cap_payload(cid, bytes(acl_buf[handle][:want]), idx, direction, ts, att_events, other_l2cap_events)
                        del acl_buf[handle]
                        del acl_want[handle]
            continue

    print("\n=== L2CAP channel usage (CID: count) ===")
    for cid, cnt in sorted(l2cap_channels.items(), key=lambda x: -x[1]):
        print(f"  CID 0x{cid:04x}: {cnt} PDUs")

    print(f"\n=== HCI Commands seen: {len(commands_seen)} (first 20) ===")
    for rec in commands_seen[:20]:
        print(rec)

    print(f"\n=== HCI Events seen: {len(events_seen)} (event code histogram) ===")
    evt_hist = defaultdict(int)
    for _, _, code, _ in events_seen:
        evt_hist[code] += 1
    for code, cnt in sorted(evt_hist.items(), key=lambda x: -x[1]):
        print(f"  event 0x{code:02x}: {cnt}")

    print(f"\n=== ATT PDUs (CID 0x0004): {len(att_events)} ===")
    for rec in att_events:
        print(rec)

    print(f"\n=== Other L2CAP PDUs (non-ATT): {len(other_l2cap_events)} (first 40) ===")
    for rec in other_l2cap_events[:40]:
        print(rec)

    return records, att_events, other_l2cap_events

def handle_l2cap_payload(cid, payload, idx, direction, ts, att_events, other_l2cap_events):
    if cid == 0x0004:
        att_events.append((idx, direction, ts, hexdump(payload, 200)))
    else:
        other_l2cap_events.append((idx, direction, cid, ts, hexdump(payload, 200)))

if __name__ == "__main__":
    parse(sys.argv[1])
