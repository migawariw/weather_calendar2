import requests
from ics import Calendar, Event
import datetime
import os

LAT = 35.6619
LON = 139.7024

def wmo_to_text(code):
    weather_map = {
        0: "快晴", 1: "晴れ", 2: "所により曇り", 3: "曇り",
        45: "霧", 48: "着氷性の霧",
        51: "弱い霧雨", 53: "霧雨", 55: "強い霧雨",
        61: "弱い雨", 63: "雨", 65: "強い雨",
        71: "弱い雪", 73: "雪", 75: "強い雪",
        80: "弱いにわか雨", 81: "にわか雨", 82: "強いにわか雨",
        95: "雷雨"
    }
    return weather_map.get(code, "不明な天気")

def fetch_and_create_ics(start_date, end_date, filepath):
    # 指定された期間のデータを取得してicsファイルを保存する関数
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=weather_code,temperature_2m_mean,precipitation_sum&timezone=Asia%2FTokyo&start_date={start_date}&end_date={end_date}"
    res = requests.get(url).json()

    cal = Calendar()
    daily = res['daily']

    for i in range(len(daily['time'])):
        e = Event()
        e.name = f"{wmo_to_text(daily['weather_code'][i])} {daily['temperature_2m_mean'][i]:.1f}℃"
        e.description = f"降水量: {daily['precipitation_sum'][i]}mm"
        e.begin = daily['time'][i]
        e.make_all_day()
        cal.events.add(e)

    # イベントを日付順（古い順）に並び替える
    cal.events = sorted(cal.events, key=lambda e: e.begin)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(cal.serialize_iter())

def main():
    today = datetime.date.today()
    os.makedirs("calendars", exist_ok=True)

    # 1. 常時更新する「直近過去1ヶ月分」のweather.icsを作成
    #（今日から30日前までの期間）
    start_30days_ago = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    end_today = today.strftime("%Y-%m-%d")
    fetch_and_create_ics(start_30days_ago, end_today, "calendars/weather.ics")

    # 2. 毎月1日だけ、前月分の確定データを「年-月.ics」として書き出し
    # (例: 7月1日なら6月1日〜30日分のデータを作成)
    # if today.day == 1:
    if True:
        # 前月の最後の日の情報から、前月の年と月を取得
        last_day_of_last_month = today - datetime.timedelta(days=1)
        last_month_year = last_day_of_last_month.year
        last_month = last_day_of_last_month.month
        
        # 前月の1日から最終日までの期間を設定
        start_last_month = last_day_of_last_month.replace(day=1).strftime("%Y-%m-%d")
        end_last_month = last_day_of_last_month.strftime("%Y-%m-%d")
        
        filename = f"{last_month_year}-{last_month}.ics"
        fetch_and_create_ics(start_last_month, end_last_month, f"calendars/{filename}")

if __name__ == "__main__":
    main()
