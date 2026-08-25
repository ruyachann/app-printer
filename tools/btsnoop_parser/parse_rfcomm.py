#!/usr/bin/env python3
"""Extract L2CAP PDUs per CID and decode RFCOMM UIH payloads."""
import struct
import sys
from collections import defaultdict

def read_records(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"btsnoop\x00"
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

def l2cap_pdus(records):
    """Yield (idx, direction, cid, payload_bytes) for every complete L2CAP PDU."""
    acl_buf = {}
    acl_want = {}
    for idx, (ts, flags, pkt) in enumerate(records):
        if not pkt or pkt[0] != 0x02:
            continue
        direction = "A->B" if not (flags & 0x01) else "B->A"
        body = pkt[1:]
        if len(body) < 4:
            continue
        handle_flags, data_len = struct.unpack("<HH", body[0:4])
        handle = handle_flags & 0x0FFF
        pb = (handle_flags >> 12) & 0x3
        acl_payload = body[4:4+data_len]
        if pb in (0b10, 0b00):
            if len(acl_payload) < 4:
                continue
            l2cap_len, cid = struct.unpack("<HH", acl_payload[0:4])
            sdu = acl_payload[4:]
            if len(sdu) >= l2cap_len:
                yield (idx, direction, cid, sdu[:l2cap_len])
            else:
                acl_buf[handle] = bytearray(sdu)
                acl_want[handle] = (cid, l2cap_len)
        elif pb == 0b01:
            if handle in acl_buf:
                acl_buf[handle].extend(acl_payload)
                cid, want = acl_want[handle]
                if len(acl_buf[handle]) >= want:
                    yield (idx, direction, cid, bytes(acl_buf[handle][:want]))
                    del acl_buf[handle]
                    del acl_want[handle]

RFCOMM_FRAME_TYPES = {
    0x2F: "SABM",
    0x63: "UA",
    0x0F: "DM",
    0x43: "DISC",
    0xEF: "UIH",
    0x03: "UI",
}

def decode_rfcomm(payload):
    if len(payload) < 3:
        return None
    addr = payload[0]
    ctrl = payload[1]
    dlci = (addr >> 2) & 0x3F
    frame_type = ctrl & ~0x10  # mask poll/final bit
    ftype_name = RFCOMM_FRAME_TYPES.get(frame_type, f"0x{frame_type:02x}")
    off = 2
    if off >= len(payload):
        return None
    len_byte = payload[off]
    if len_byte & 0x01:
        length = len_byte >> 1
        off += 1
    else:
        if off + 1 >= len(payload):
            return None
        length = (len_byte >> 1) | (payload[off+1] << 7)
        off += 2
    info = payload[off:off+length]
    return dlci, ftype_name, info

def ascii_repr(b):
    return "".join(chr(c) if 32 <= c < 127 else "." for c in b)

def main(path, target_cids=None):
    records = read_records(path)
    by_cid = defaultdict(list)
    for idx, direction, cid, payload in l2cap_pdus(records):
        by_cid[cid].append((idx, direction, payload))

    print("=== CID summary ===")
    for cid, items in sorted(by_cid.items(), key=lambda x: -len(x[1])):
        print(f"CID 0x{cid:04x}: {len(items)} PDUs, first idx={items[0][0]}, last idx={items[-1][0]}")

    if target_cids is None:
        target_cids = sorted(by_cid.keys(), key=lambda c: -len(by_cid[c]))[:6]

    for cid in target_cids:
        print(f"\n\n########## CID 0x{cid:04x} ({len(by_cid[cid])} PDUs) ##########")
        for idx, direction, payload in by_cid[cid]:
            decoded = decode_rfcomm(payload)
            if decoded is None:
                print(f"[{idx}] {direction} raw(len={len(payload)}): {payload[:80].hex()}")
                continue
            dlci, ftype, info = decoded
            info_hex = info.hex()
            info_ascii = ascii_repr(info)
            print(f"[{idx}] {direction} DLCI={dlci} {ftype} len={len(info)}")
            if info:
                print(f"    hex: {info_hex[:240]}{'...' if len(info_hex)>240 else ''}")
                print(f"    asc: {info_ascii[:120]}{'...' if len(info_ascii)>120 else ''}")

if __name__ == "__main__":
    path = sys.argv[1]
    cids = None
    if len(sys.argv) > 2:
        cids = [int(x, 16) for x in sys.argv[2:]]
    main(path, cids)
