import http
import mimetypes
import os
from unicodedata import normalize

import requests


class ApiDriver:

    def __init__(self, token, api):
        self.token = token
        self.header = {
            "User-Agent": "JuniorCandidateTestApp (vlad2284222@gmail.com)/0.7",
            "Authorization": "Bearer "+token
        }
        self.api = api
        try:
            res = requests.get(self.api+"accounts", headers=self.header)
            if res.status_code != 401:
                self.id = res.json()["items"][0]["id"]
            else:
                raise
        except Exception as e:
            raise AttributeError("Couldn't connect to server")

    def check(self):
        res = requests.get(self.api+'me', headers=self.header)
        return res.ok

    def add_applicant(self, data, file_response=None):
        json = {
            "last_name": data["full_name"].split()[0],
            "first_name": data["full_name"].split()[1],
            "money": data["wage"],
            "position": data["position"]
        }

        if file_response is not None:
            json["externals"] = [{
                "data": {
                    "body": file_response["text"]
                },
                "auth_type": "NATIVE",
                "files": [
                {
                    "id": file_response["file_id"]
                }
                ],
            }]
            if file_response.get("name") is not None:
                json["last_name"] = file_response["name"].get("last")
                json["first_name"] = file_response["name"].get("first")
                json["middle_name"] = file_response["name"].get("middle")
            if file_response.get("birthdate") is not None:
                json["birthday_day"] = file_response["birthdate"].get("day")
                json["birthday_month"] = file_response["birthdate"].get("month")
                json["birthday_year"] = file_response["birthdate"].get("year")
            if file_response.get("photo_id") is not None:
                json["photo"] = file_response.get("photo_id")
            if file_response.get("email") is not None:
                json["email"] = file_response["email"]
            if file_response.get("phones") is not None:
                json["phone"] = file_response["phones"].pop()

        url = self.api + "account/" + str(self.id) + "/applicants"
        res = requests.post(url, headers=self.header, json=json)
        if res.ok:
            res = res.json()
            return res["id"]
        else:
            raise RuntimeError("Couldn't add applicant")

    def add_file(self, file):
        header = self.header
        header["X-File-Parse"] = "true"
        url = self.api+"account/" + str(self.id) + "/upload"
        mt = mimetypes.guess_type(file)[0]
        buffer = open(file, 'rb')
        files = {'file': (os.path.basename(file), buffer, mt)}
        res = requests.post(url, headers=header, files=files)
        buffer.close()
        if res.ok:
            res = res.json()
            ans = {
                "file_id" : res["id"],
                "text" : res["text"],
            }
            if res["photo"] is not None:
                ans["photo_id"] = res["photo"]["id"]
            if res["fields"] is not None:
                if res["fields"].get("name") is not None:
                    ans["name"] = res["fields"]["name"]
                if res["fields"].get("position") is not None:
                    ans["position"] = res["fields"]["position"]
                if res["fields"].get("email") is not None:
                    ans["email"] = res["fields"]["email"]
                if res["fields"].get("phones") is not None:
                    ans["phones"] = res["fields"]["phones"]
                if res["fields"].get("salary") is not None:
                    ans["salary"] = res["fields"]["salary"]
                if res["fields"].get("birthdate") is not None:
                    ans["birthdate"] = res["fields"]["birthdate"]
            return ans
        else:
            raise RuntimeError("Couldn't upload file")

    def match_vacancy_and_candidate(self, applicant_id, position, status, comment, file_id=None):

        url = self.api + "account/{}/vacancies".format(self.id)
        res = requests.get(url, headers=self.header, params={"opened": True})
        if not res.ok:
            raise RuntimeError("Couldn't get vacancies")
        res = res.json()
        vacancy_id = None
        for vacancy in res["items"]:
            if normalize("NFKC", vacancy["position"]) == position:
                vacancy_id = vacancy["id"]
                break
        if vacancy_id is None:
            raise RuntimeError("Couldn't get vacancies")

        url = self.api + "account/{}/vacancy/statuses".format(self.id)
        res = requests.get(url, headers=self.header,)
        if not res.ok:
            raise RuntimeError("Couldn't get statuses")
        res = res.json()
        status_id = None
        for possible_status in res["items"]:
            if normalize("NFKC", possible_status["name"]) == status:
                status_id = possible_status["id"]
                break
        if status_id is None:
            raise RuntimeError("Couldn't get statuses")

        url = self.api + "account/{}/applicants/{}/vacancy".format(self.id, applicant_id)
        json = {
            "vacancy": vacancy_id,
            "status": status_id,
            "comment": comment,
        }
        if file_id is not None:
            json["files"] = [
                {
                    "id": 1382810
                }
                ]
        res = requests.post(url, headers=self.header, json=json)
        if not res.ok:
            raise RuntimeError("Couldn't add applicant to vacancy")
