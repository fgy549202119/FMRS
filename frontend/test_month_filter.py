from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})

    print('=== Test: Evaluation month filter API (no auth) ===')
    page.goto('http://localhost:3000/login')
    page.wait_for_load_state('networkidle')

    result = page.evaluate("""
        async () => {
            const tests = {};

            try {
                const res1 = await fetch('/api/repair/evaluations/?page_size=10');
                const data1 = await res1.json();
                tests.noFilter = {
                    status: res1.status,
                    count: data1.count || 0,
                    results: (data1.results || []).map(r => ({id: r.id, created_at: r.created_at, staff_id: r.staff_id}))
                };
            } catch (e) {
                tests.noFilter = { error: e.message };
            }

            try {
                const res2 = await fetch('/api/repair/evaluations/?page_size=10&month=2026-04');
                const data2 = await res2.json();
                tests.aprilFilter = {
                    status: res2.status,
                    count: data2.count || 0,
                    results: (data2.results || []).map(r => ({id: r.id, created_at: r.created_at}))
                };
            } catch (e) {
                tests.aprilFilter = { error: e.message };
            }

            try {
                const res3 = await fetch('/api/repair/evaluations/?page_size=10&month=2026-03');
                const data3 = await res3.json();
                tests.marchFilter = {
                    status: res3.status,
                    count: data3.count || 0
                };
            } catch (e) {
                tests.marchFilter = { error: e.message };
            }

            return tests;
        }
    """)

    print(f'No filter: count={result.get("noFilter", {}).get("count", "N/A")}')
    for r in result.get('noFilter', {}).get('results', []):
        print(f'  id={r.get("id")}, created_at={r.get("created_at")}, staff_id={r.get("staff_id")}')

    print(f'\\nApril filter: count={result.get("aprilFilter", {}).get("count", "N/A")}')
    for r in result.get('aprilFilter', {}).get('results', []):
        print(f'  id={r.get("id")}, created_at={r.get("created_at")}')

    print(f'\\nMarch filter: count={result.get("marchFilter", {}).get("count", "N/A")}')

    browser.close()
    print('\\n=== Test Complete ===')
