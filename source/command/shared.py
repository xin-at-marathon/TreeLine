
FIELDS = ["outputlines","spacebetween","formathtml"]

def merge_formats(struct_formats, view_formats):
    merged_formats = []
    for sf in struct_formats:
        name = sf['formatname']

        found = None
        for vf in view_formats:
            if name == vf['formatname']:
                found = vf
                break
            
        if found:
            for f in FIELDS:
                if f in found:
                    sf[f] = found[f]
                else:
                    if f in sf:
                        del sf[f]

        merged_formats.append(sf)
                
    return merged_formats
