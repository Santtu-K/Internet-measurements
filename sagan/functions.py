import pyasn

asndb = pyasn.pyasn("ipasn_db.dat")

def get_total_allocatable_ips(asn):
    prefixes = asndb.get_as_prefixes(asn)
    if not prefixes:
        print(f"ASN {asn} not found.")
        return 0
    #print("prefixes",prefixes)
    #mask = [int(p.split('/')[1]) for p in prefixes]
    #print("masks", mask)
    total = sum(2**(32 - int(p.split('/')[1])) for p in prefixes)
    #print(f"ASN {asn} has {len(prefixes)} prefix(es), allocates {total} usable IP addresses.")
    return total