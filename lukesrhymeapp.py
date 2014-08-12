import re
import string
import types
from urllib2 import urlopen
import cgi #Think vgi not cgi... (rstuvw)
import webapp2

myAddress = "ftp://ftp.cs.cmu.edu/project/fgdata/dict/cmudict.0.6"
htmlPage = urlopen(myAddress)
htmlText = htmlPage.read().lower()

def stripNumbers(String):
    for n in range(10):
        String = string.replace(String, str(n), "")
    return String

def getWord(word):
    matchResults = re.search(r"\b{} ( [a-z]*[0-2]*)*".format(word), htmlText, re.IGNORECASE) #That worked suprisingly well...
    if type(matchResults) == types.NoneType:
        return "WORD NOT FOUND"
    return matchResults.group()

vowelSounds = ["aa", "ae", "ah", "ao", "aw", "ay", "eh", "er", "ey", "ih", "iy", "ow", "oy", "uh", "uw"]

def getSyllables(word): #Uses the vowel rule. Does not return what you would expect.
    check = getWord(word)
    if check == "WORD NOT FOUND":
        return "WORD NOT FOUND"
    phonemes = check.split("  ")[1]
    syllables = []
    phonemes = stripNumbers(phonemes)
    phonemes = phonemes.split(" ")
    L = len(phonemes) - 1
    old = L + 1
    for a in range(L + 1): #Actually goes through from end to front, since the ending syllable is what matters; the rest is stored purely for counting.
        for b in vowelSounds:
            if phonemes[L - a] == b:
                syllables.append(phonemes[L - a:old])
                old = L - a
                break
    return syllables

def gatherInfo(word): #Tells the user the syllable count and pronunciation as well as a list of words which end-syllable rhyme with it.
    if word == "":
        return ""
    check = getSyllables(word)
    if check == "WORD NOT FOUND":
        return "WORD NOT FOUND"
    syllables = check
    syllableCount = len(syllables)
    lastSyllable = syllables[0]
    pronunciation = getWord(word).split("  ")[1]
    for n in range(10):
        pronunciation = string.replace(pronunciation, str(n), "")
    String = ""
    for a in lastSyllable:
        String += " " + a + r"[0-2]*"
    search = r"\n.*" + String + r"\n"
    results = re.findall(search, htmlText, re.IGNORECASE)
    fResults = [[]]
    for a in results:
        count = 0
#        explode = a.replace("\n", "").split("  ") The darn site occasionally missed the "  " with just " ". So I need to manually deal with that...
        tempPhenomes = stripNumbers(a).replace("\n", "").replace("  ", " ").split(" ")
        tempWord = tempPhenomes.pop(0)
        for a in tempPhenomes:
            for b in vowelSounds:
                if a == b:
                    count += 1 #Same result as len(getSyllables(tempWord)), but this does substantially less work.
        tempWord = re.sub("{.*?}", "", tempWord.replace("(", "{").replace(")", "}"))
        while len(fResults) < count:
            fResults.append([])
        fResults[count - 1].append(tempWord)
    tables = ""
    for a in range(0, len(fResults) - 1):
        table = '<caption><b>{} Syllables:</b><br></caption><table style = "width:1100px">'.format(a + 1)
        length = 0
        L = len(fResults[a])
        while length + 12 <= L:
            table += "<tr>"
            for b in range(12):
                table += "<td>{}</td>".format(fResults[a][length])
                length += 1
                if length > L:
                    break
            table += "</tr>"
        tables += table + "</table><br>"
    baseInfo = """<b>Number of syllables: {} <br>
Pronunciation: {} <br><br>Words which rhyme with {}:</b><br><br>""".format(syllableCount, pronunciation, word.lower())
    return baseInfo + tables

class MainPage(webapp2.RequestHandler):
    def get(self):
        word = cgi.escape(self.request.get("word"))
        tables = gatherInfo(word)
        script = """
<html>
<head>
<title>Luke's Rhyming Tool</title>
</head>
<body bgcolor = "#DDDDDD">
<H1>Luke's Rhyming Tool</H1>
<H3>This is a simple tool which can find words which rhyme with and count syllables for any word found in the helpful <a href = "ftp://ftp.cs.cmu.edu/project/fgdata/dict/cmudict.0.6">Carnegie Mellon Pronouncing Dictionary</a>.<br>
The source code can be found <a href = https://www.dropbox.com/sh/d06rlm52dfcx5bf/AABPawGoaahOiJaUNnuQdFl4a> here </a>.
</H3>
<form action="/" method="get">
<b>Enter word here: </b><input type="text"
name="word" value={}>
<input type="submit" value="Submit"><br><br>
{}
</form >
</body >
</html >""".format(word.lower(), tables)
        self.response.headers["Content-Type"] = "text/html"
        self.response.write(script)

routes = [('/', MainPage)]
myApp = webapp2.WSGIApplication(routes, debug=True)
