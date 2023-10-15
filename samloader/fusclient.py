# SPDX-License-Identifier: GPL-3.0+
# Copyright (C) 2020 nlscc

""" FUS request helper (automatically sign requests and update tokens) """

import requests

from . import auth

class FUSClient:
    """ FUS API client. """
    def __init__(self):
        self.auth = ""
        self.sessid = ""
        self.makereq("NF_DownloadGenerateNonce.do") # initialize nonce
    def makereq(self, path: str, data: str = "") -> str:
        """ Make a FUS request to a given endpoint. """
        authv = 'FUS nonce="", signature="' + self.auth + '", nc="", type="", realm="", newauth="1"'
        req = requests.post("https://neofussvr.sslcs.cdngc.net/" + path, data=data,
                            headers={"Authorization": authv, "User-Agent": "Kies2.0_FUS"},
                            cookies={"JSESSIONID": self.sessid})
        # If a new NONCE is present, decrypt it and update our auth token.
        if "NONCE" in req.headers:
            self.encnonce = req.headers["NONCE"]
            self.nonce = auth.decryptnonce(self.encnonce)
            self.auth = auth.getauth(self.nonce)
        # Update the session cookie if needed.
        if "JSESSIONID" in req.cookies:
            self.sessid = req.cookies["JSESSIONID"]
        req.raise_for_status()
        return req.text
    def downloadfile(self, filename: str, start: int = 0) -> requests.Response:
        """ Make a FUS cloud request to download a given file. """
        # In a cloud request, we also need to pass the server nonce.
        authv = 'FUS nonce="' + self.encnonce + '", signature="' + self.auth \
            + '", nc="", type="", realm="", newauth="1"'
        headers = {"Authorization": authv, "User-Agent": "Kies2.0_FUS"}
        if start > 0:
            headers["Range"] = "bytes={}-".format(start)
        req = requests.get("http://cloud-neofussvr.samsungmobile.com/NF_DownloadBinaryForMass.do",
                           params="file=" + filename, headers=headers, stream=True)
        req.raise_for_status()
        return req
