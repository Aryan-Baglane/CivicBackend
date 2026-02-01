from googlesearch import search
try:
    results = list(search("Municipal Corporation Delhi official contact helpline email", num_results=3))
    print(f"Results found: {len(results)}")
    for r in results:
        print(r)
except Exception as e:
    print(f"Error: {e}")
