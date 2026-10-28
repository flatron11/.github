import time
from datetime import datetime
import requests

# Beállítások
BASE_CURRENCY = "EUR"  # Mihöz képest (vagy fordítva)
TARGET_CURRENCY = "HUF"
# Adj meg egy céltartományt vagy árat, aminél már váltanál (pl. ha 1 EUR < 390 HUF)
TARGET_RATE_THRESHOLD = 390.0
CHECK_INTERVAL_SECONDS = 300  # 5 percenkénti ellenőrzés


def get_current_huf_eur_rate():
  """Lekéri az aktuális középárfolyamot (ami a Revolut alapja is hétköznap)"""
  url = f"https://api.frankfurter.dev/v1/latest?base={BASE_CURRENCY}&symbols={TARGET_CURRENCY}"
  try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    rate = data["rates"][TARGET_CURRENCY]
    return rate
  except Exception as e:
    print(f"Hiba történt az árfolyam lekérdezésekor: {e}")
    return None


def monitor_market():
  print(
      f"--- Revolut HUF/EUR Árfolyamfigyelő elindult ---"
      f" ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
  )
  print(f"Cél árfolyam küszöb: {TARGET_RATE_THRESHOLD} HUF / 1 EUR alatt\n")

  lowest_seen = float("inf")
  highest_seen = 0.0

  try:
    while True:
      current_rate = get_current_huf_eur_rate()
      current_time = datetime.now().strftime("%H:%M:%S")

      if current_rate:
        # Frissítjük a minimum/maximum értéket a futás alatt
        if current_rate < lowest_seen:
          lowest_seen = current_rate
        if current_rate > highest_seen:
          highest_seen = current_rate

        print(
            f"[{current_time}] Jelenlegi árfolyam: 1 EUR = {current_rate:.2f}"
            f" HUF (Eddigi min: {lowest_seen:.2f} | max: {highest_seen:.2f})"
        )

        # Ha az árfolyam a megadott küszöbérték alá esett (azaz olcsóbb lett az euró)
        if current_rate <= TARGET_RATE_THRESHOLD:
          print("\n" + "=" * 50)
          print(
              f"🎉 FIGYELEM! Az EUR árfolyam elérte a kívánt szintet!"
              f" ({current_rate:.2f} HUF)"
          )
          print("Itt az ideje átváltani a pénzt a Revolutban!")
          print("=" * 50 + "\n")
          # Itt akár küldhetsz magadnak Telegram / Discord üzenetet is, ha szeretnéd.

      # Várakozás a következő ellenőrzésig
      time.sleep(CHECK_INTERVAL_SECONDS)

  except KeyboardInterrupt:
    print("\nA figyelést leállítottad. Jó utat a váltáshoz!")


if __name__ == "__main__":
  monitor_market()