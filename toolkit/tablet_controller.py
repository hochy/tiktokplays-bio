#!/usr/bin/env python3
"""
Tablet Controller Toolkit
Automates Android / Fire OS interactions via uiautomator2 and ADB.
"""

import sys
import os
import re
import json
import time

try:
    import uiautomator2 as u2
except ImportError:
    print("uiautomator2 not installed in current environment.")
    sys.exit(1)

class TabletController:
    def __init__(self, serial=None):
        self.device = u2.connect(serial)
        self.device.screen_on()
        
    def info(self):
        return self.device.info

    def wake(self):
        self.device.screen_on()
        self.device.shell("svc power stayon true")
        self.device.shell("settings put system screen_off_timeout 1800000")

    def unlock_pin(self, pin: str):
        self.wake()
        for digit in pin:
            self.device(text=str(digit)).click()
            time.sleep(0.1)

    def screenshot(self, output_path: str):
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        img = self.device.screenshot()
        img.save(output_path)
        return output_path

    def current_app(self):
        return self.device.app_current()

    def launch_tiktok(self):
        self.wake()
        self.device.app_start("com.zhiliaoapp.musically", stop=False)
        time.sleep(3)

    def get_screen_elements(self):
        xml = self.device.dump_hierarchy()
        elements = []
        pattern = r'<node\s+([^>]+)/>|<node\s+([^>]+)>'
        matches = re.findall(pattern, xml)
        for m1, m2 in matches:
            attr_str = m1 or m2
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', attr_str))
            text = attrs.get("text", "").strip()
            desc = attrs.get("content-desc", "").strip()
            res_id = attrs.get("resource-id", "").strip()
            clickable = attrs.get("clickable", "false") == "true"
            bounds = attrs.get("bounds", "")
            if text or desc or (clickable and res_id):
                elements.append({
                    "text": text,
                    "desc": desc,
                    "id": res_id,
                    "clickable": clickable,
                    "bounds": bounds
                })
        return elements

    def click(self, text=None, desc=None, res_id=None):
        if text:
            el = self.device(text=text)
            if el.exists:
                el.click()
                return True
            el_contains = self.device(textContains=text)
            if el_contains.exists:
                el_contains.click()
                return True
        if desc:
            el = self.device(description=desc)
            if el.exists:
                el.click()
                return True
        if res_id:
            el = self.device(resourceId=res_id)
            if el.exists:
                el.click()
                return True
        return False

    def scroll_down(self):
        self.device.swipe_ext("up", scale=0.6)

    def scroll_up(self):
        self.device.swipe_ext("down", scale=0.6)

if __name__ == "__main__":
    t = TabletController()
    print("Device Info:", json.dumps(t.info(), indent=2))
    print("Current App:", json.dumps(t.current_app(), indent=2))
