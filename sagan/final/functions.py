import pyasn

asndb = pyasn.pyasn("ipasn_db.dat")

# helper function to get the number of allocated IP @s by an AS
def get_total_allocatable_ips(asn):
    prefixes = asndb.get_as_prefixes(asn)
    if not prefixes:
        print(f"ASN {asn} not found.")
        return 0
    total = sum(2**(32 - int(p.split('/')[1])) for p in prefixes)
    return total