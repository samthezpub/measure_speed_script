import argparse
import sys
import time

import requests

CHUNK_SIZE = 64 * 1024
BYTES_IN_MB = 1_000_000


# Например можно использовать ссылку Selectel (10MB)
# https://speedtest.selectel.ru/10MB
def get_img_by_url(image_url: str, timeout: float = 20.0) -> tuple[float, int]:
    total = 0
    start = time.perf_counter()

    with requests.get(image_url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            total += len(chunk)
        elapsed = time.perf_counter() - start
    return elapsed, total


def summarize(results: list[tuple[float, int]], attempts: int) -> None:
    total_time = sum(elapsed for elapsed, _ in results)
    total_bytes = sum(size for _, size in results)
    speed = total_bytes / total_time / BYTES_IN_MB  # МБ/с

    print(f"Успешных запросов: {len(results)} из {attempts}")
    print(f"Среднее время запроса: {total_time / len(results):.2f} с")
    print(f"Скачано всего: {total_bytes / BYTES_IN_MB:.2f} МБ")
    print(f"Средняя скорость: {speed:.2f} МБ/с ({speed * 8:.1f} Мбит/с)")


def main():
    parser = argparse.ArgumentParser(description="Measure speed of an image")
    parser.add_argument("url", type=str, help="Image URL")
    parser.add_argument("--count", type=int, default=10, help="number of requests")
    parser.add_argument("--timeout", type=float, default=20.0, help="Timeout for downloading image")

    args = parser.parse_args()
    if args.count < 1 or args.timeout <= 0:
        parser.error("count must be >= 1 and timeout must be > 0")

    results: list[tuple[float, int]] = []
    for i in range(1, args.count + 1):
        try:
            elapsed, size = get_img_by_url(args.url, timeout=args.timeout)
        except requests.RequestException as e:
            print(f"Запрос {i}: ошибка: {e}")
            continue
        results.append((elapsed, size))
        print(f"Запрос {i}: {elapsed:.2f} с, {size / BYTES_IN_MB:.2f} МБ, "
              f"{size / elapsed / BYTES_IN_MB:.2f} МБ/с")

    if not results:
        sys.exit("Ни один запрос не удался")
    summarize(results, args.count)


if __name__ == '__main__':
    main()