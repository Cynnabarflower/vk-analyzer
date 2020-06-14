import requests
import bs4
import re
import json
import random
import time

"""
Class by Dmitry Podbolotov
"""
class VKFA:

    def __init__(self, login=None, passwd=None, obj=None, section=None, **kwargs):
        self.login = login
        self.password = passwd
        self.kwargs = kwargs
        self.s = requests.session()

        self.obj = obj
        self.section = section

    def auth(self):
        """
        Authentification
        :return:
        :rtype:
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded"
        }
        self.s.headers = headers
        r = self.s.get("https://vk.com/")

        soup = bs4.BeautifulSoup(r.text, "html.parser")
        params = {}
        for i in soup.find("form", {"id": "quick_login_form"}).findAll("input"):
            params[i.get("name")] = i.get("value")
        params["email"] = self.login
        params["pass"] = self.password
        del params[None]
        r = self.s.post("https://login.vk.com/?act=login", params=params)
        if "onLoginDone" in r.text:
            line = re.search(r"parent.onLoginDone\((.+)\);", r.text).group(0)
            data = re.match(r"[^[]*\(([^]]*)\)", line).groups()[0]
            self.url = "http://vk.com" + data.split(",")[0].replace("'", "")
            return self.url
        else:
            return False

    def __getattr__(self, method):
        if self.obj:
            obj = self.obj
        else:
            obj = self

        if self.section:
            return VKFA(section=f"{self.section}.{method}", obj=obj)
        else:
            return VKFA(section=method, obj=self)

    def __call__(self, **kwargs):
        h = self.obj.get_hash(self.section)
        if not h:
            raise Exception("Error while getting hash")
        params = {
            "act": "a_run_method",
            "al": 1,
            "hash": h,
            "param_v": "5.103",
            "method": self.section
        }

        for i in self.obj.kwargs:
            params[f"param_{i}"] = self.obj.kwargs[i]

        for i in kwargs:
            params[f"param_{i}"] = kwargs[i]

        r = self.obj.s.get(f"https://vk.com/dev/{self.section}", params=params)
        try:
            data = json.loads(json.loads(re.findall("<!--(.+)", r.text)[0])["payload"][1][0])
            if "response" in data:
                return data["response"]
            raise Exception(data["error"])
        except Exception as e:
            return e

    def get_hash(self, method):
        r = self.s.get('https://vk.com/dev/' + method)
        h = re.findall('onclick="Dev.methodRun\(\'(.+?)\', this\);', r.text)
        if h:
            return h
        return False
