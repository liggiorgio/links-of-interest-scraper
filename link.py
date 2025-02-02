from bs4 import BeautifulSoup as bs
import requests
import json


class CDL():
    def __init__(self, name, link):
        self.name = name
        self.link = link
    

SKIP = [
    "Progettazione delle aree verdi e del paesaggio - Interateneo",
    "Scienze viticole ed enologiche - Interateneo",
    "Artificial Intelligence",
    "Interpretariato e traduzione in lingua dei segni italiana (LIS) e lingua dei segni italiana tattile (LIST)",
    "Artificial intelligence for science and technology",
    "Global Environment and Development",
]


HOME = "https://www.unimi.it"


def parser():
    data = requests.get("https://www.unimi.it/it/corsi/corsi-di-laurea-triennali-e-magistrali-ciclo-unico").text
    soup = bs(data, "lxml").find_all("a", hreflang = "it")
    cdl = [CDL(link.text.strip(), HOME + link["href"]) for link in soup][1:]

    data = requests.get("https://www.unimi.it/it/corsi/corsi-di-laurea-magistrale").text
    soup = bs(data, "lxml").find_all("a", hreflang = "it")
    cdl = cdl + [CDL(link.text.strip(), HOME + link["href"]) for link in soup][1:]

    utils = list()
    for i in range(len(cdl)):
        if cdl[i].name in SKIP:
            continue

        data = requests.get(cdl[i].link).text
        soup = bs(data, "lxml")
        files = soup.find_all("span", class_ = "file-link")

        sm = files[0].find("a")["href"]
        rules = files[1].find("a")["href"] if len(files) > 1 else None
        aus = files[3].find("a")["href"] if len(files) > 1 else None
        
        div = soup.find("div", class_ = "views-field views-field-bando-al-servizio")
        links = [link["href"].strip() for link in div.findChildren("a", recursive=True)]

        imm = dict()
        if len(links) == 1:
            imm["Immatricolazione"] = links[0]
        elif len(links) == 2:
            imm["Domanda di ammissione"] = links[0]
            imm["Immatricolazione"] = links[1]
        else:
            imm["Domanda di ammissione"] = links[0]
            imm["Graduatoria"] = links[1]
            imm["Immatricolazione"] = links[2]
        
        utils.append({
            "Nome" : cdl[i].name,
            "Link" : cdl[i].link,
            "Manifesto degli studi" : sm,
            "Regolamento didattico" : rules,
            "Scheda unica annuale" : aus,
            "Immatricolazione" : imm
        })
    
    return utils
        

def main():
    f = open("links.json", "w")
    f.write(json.dumps(parser()))
    f.close()


if __name__ == "__main__":
    main()