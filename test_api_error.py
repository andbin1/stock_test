"""测试 API 错误"""
from app_with_cache import app
import json

print("测试 /api/cache/stocks 端点...")
print("="*60)

with app.test_client() as client:
    try:
        response = client.get('/api/cache/stocks')
        print(f"Status Code: {response.status_code}")

        try:
            data = response.get_json()
            print(f"Success: {data.get('success')}")

            if not data.get('success'):
                print(f"\n❌ API返回错误:")
                print(f"Error: {data.get('error')}")
            else:
                print(f"\n✅ API返回成功:")
                print(f"Total: {data.get('total')}")
                print(f"Stocks: {len(data.get('stocks', []))}")

        except Exception as e:
            print(f"\n❌ JSON解析错误:")
            print(f"Exception: {e}")
            print(f"Response text: {response.get_data(as_text=True)[:500]}")

    except Exception as e:
        print(f"\n❌ 请求异常:")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception: {e}")

        import traceback
        print("\n完整堆栈:")
        traceback.print_exc()
