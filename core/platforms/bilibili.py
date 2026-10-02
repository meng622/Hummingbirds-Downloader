import os
import re

import requests


class BilibiliDanmaku:
    """B站彈幕下載器。"""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com/",
    }

    def __init__(self, cookie_path: str = ""):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        if cookie_path and os.path.isfile(cookie_path):
            self._load_cookies(cookie_path)

    def _load_cookies(self, path: str):
        """載入 Netscape 格式 cookies.txt。"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.strip().split("\t")
                    if len(parts) >= 7:
                        self.session.cookies.set(parts[5], parts[6], domain=parts[0])
        except Exception:
            pass

    # ---------- cid 獲取 ----------

    def get_cid(self, bvid: str) -> int | None:
        """用 B站 API 攞影片 cid。"""
        url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp"
        try:
            r = self.session.get(url, timeout=10)
            data = r.json()
            if data.get("code") == 0 and data["data"]:
                return data["data"][0]["cid"]
        except Exception:
            pass
        return None

    @staticmethod
    def extract_bvid(url: str) -> str | None:
        m = re.search(r"(BV[0-9A-Za-z]+)", url)
        return m.group(1) if m else None

    # ---------- 彈幕 XML 獲取 ----------

    def download_danmaku_xml(self, cid: int, output_dir: str) -> str | None:
        """下載彈幕 XML 檔案，返回檔案路徑。"""
        xml_url = f"https://comment.bilibili.com/{cid}.xml"
        try:
            r = self.session.get(xml_url, timeout=15)
            r.encoding = "utf-8"
            if r.status_code == 200 and "<d " in r.text:
                os.makedirs(output_dir, exist_ok=True)
                out_path = os.path.join(output_dir, f"danmaku_{cid}.xml")
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(r.text)
                return out_path
        except Exception:
            pass
        return None

    # ---------- ASS 轉換 ----------

    @staticmethod
    def xml_to_ass(xml_path: str, ass_path: str, video_width: int = 1920, video_height: int = 1080) -> tuple[bool, str]:
        try:
            from biliass import convert_to_ass
        except ImportError as e:
            return False, f"未安裝 biliass：{e}"

        try:
            with open(xml_path, "r", encoding="utf-8") as f:
                xml_text = f.read()

            ass_content = convert_to_ass(
                xml_text,
                video_width,
                video_height,
                input_format="xml",
                font_face="sans-serif",
                font_size=40.0,
                text_opacity=0.85,
                duration_marquee=12.0,
                duration_still=8.0,
            )

            with open(ass_path, "w", encoding="utf-8") as f:
                f.write(ass_content)
            return True, ""
        except Exception as e:
            return False, str(e)