def fixVorbis(path):
    with open(path, 'rb') as f:
        file = f.read()
        oggS = bytearray([0x4f, 0x67, 0x67, 0x53])
        chunks = file.split(oggS)
        if b'\x76\x6f\x72\x62\x69\x73' not in chunks[1]:
            with open(path, 'wb+') as ff:
                ff.write(oggS+oggS.join(chunks[2::]))