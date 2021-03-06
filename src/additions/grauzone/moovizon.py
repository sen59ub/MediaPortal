from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.yt_url import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def moovizonGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 850, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def moovizonListEntry(entry):
	#TYPE_TEXT, x, y, width, height, fnt, flags, string [, color, backColor, backColorSelected, borderWidth, borderColor])
	png = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/images/%s.png" % entry[3]
	if fileExists(png):
		flag = LoadPixmap(png)
		return [entry,
			(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 15, 2, 20, 20, flag),
			(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 600, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
			]
	else:
		return [entry,
			(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 600, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
			]

class moovizonGenreScreen(Screen):

	def __init__(self, session):
		self.session = session

		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultGenreScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultGenreScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.change_lang
		}, -1)

		self.keyLocked = True
		self.language = "all"
		self['title'] = Label("moovizon.com")
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("all")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		url = "http://moovizon.com"
		print url, self.language
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		genre_raw = re.findall('>Categories(.*?)>Languages', data, re.S)
		if genre_raw:
			genre = re.findall('<li\sclass=""><a\shref="/.*?/(.*?)/all">(.*?).:.*?</a></li>', genre_raw[0], re.S)
		if genre:
			self.genreliste = []
			for cat_id,genreName in genre:
				url = "http://moovizon.com/%s/%s/all" % (self.language,cat_id)
				self.genreliste.append((genreName,url))
			self.chooseMenuList.setList(map(moovizonGenreListEntry, self.genreliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def change_lang(self):
		if self.language == "de":
			self.language = "all"
		elif self.language == "all":
			self.language = "en"
		elif self.language == "en":
			self.language = "es"
		elif self.language == "es":
			self.language = "pt"
		elif self.language == "pt":
			self.language = "fr"
		elif self.language == "fr":
			self.language = "it"
		elif self.language == "it":
			self.language = "de"

		self['F2'].setText(self.language)
		print "Sprache:", self.language
		self.loadPage()

	def keyOK(self):
		if self.keyLocked:
			return
		moovizonGenre = self['genreList'].getCurrent()[0][0]
		moovizonUrl = self['genreList'].getCurrent()[0][1]
		print moovizonGenre, moovizonUrl
		self.session.open(moovizonFilmListeScreen, moovizonGenre, moovizonUrl)

	def keyCancel(self):
		self.close()

class moovizonFilmListeScreen(Screen):

	def __init__(self, session, genreName, genreLink):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self.keyLocked = True
		self.page = 0
		self['title'] = Label("moovizon.com")
		self['ContentTitle'] = Label("%s:" % self.genreName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F1'].hide()
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("1")
		self['page'] = Label("")
		self['handlung'] = Label("")
		self.videoPrio = int(config.mediaportal.youtubeprio.value)-1
		self.videoPrioS = ['L','M','H']
		self.setVideoPrio()

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def setVideoPrio(self):
		if self.videoPrio+1 > 2:
			self.videoPrio = 0
		else:
			self.videoPrio += 1

	def loadPage(self):
		self.keyLocked = True
		url = "%s?page=%s" % (self.genreLink,str(self.page))
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		countp = re.findall('totalPages: (.*?),', data, re.S)
		if countp:
			self['page'].setText(countp[0])

		movies = re.findall('<li><a\shref="(/movie/.*?)"><img.*?src="(.*?)"\salt=".*?"\sclass="cover"></a>.*?<h2>(.*?)</h2><img.*?src="http://static.moovizon.com/img/flag/(.*?).png"',data, re.S)
		if movies:
			self.filmliste = []
			for (url,image,title,lang) in movies:
				url = "http://moovizon.com%s" % url.replace('&amp;','&')
				self.filmliste.append((decodeHtml(title),url,image,lang))
			self.chooseMenuList.setList(map(moovizonListEntry, self.filmliste))
			self.loadPic()
			self['Page'].setText(str(self.page+1)+" von")
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def loadPic(self):
		streamPic = self['liste'].getCurrent()[0][2]
		downloadPage(streamPic, "/tmp/Icon.jpg").addCallback(self.ShowCover)

	def ShowCover(self, picData):
		if fileExists("/tmp/Icon.jpg"):
			self['coverArt'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['coverArt'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/Icon.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['coverArt'].instance.setPixmap(ptr)
					self['coverArt'].show()
					del self.picload

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 1:
			self.page -= 1
			self.loadPage()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		self.page += 1
		self.loadPage()

	def keyLeft(self):
		if self.keyLocked:
			return
		self['liste'].pageUp()
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['liste'].pageDown()
		self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['liste'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['liste'].down()
		self.loadPic()

	def keyOK(self):
		if self.keyLocked:
			return
		self.moovizonName = self['liste'].getCurrent()[0][0]
		moovizonurl = self['liste'].getCurrent()[0][1]
		print self.moovizonName, moovizonurl
		getPage(moovizonurl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_stream).addErrback(self.dataError)

	def get_stream(self, data):
		youtube_url = re.findall('href="http://www.youtube.com/embed/(.*?)\?', data, re.S)
		if youtube_url:
			print youtube_url[0]
			y = youtubeUrl(self.session)
			y.addErrback(self.youtubeErr)
			stream = y.getVideoUrl(youtube_url[0], self.videoPrio)
			if stream:
				self.session.open(SimplePlayer, [(self.moovizonName, stream)], showPlaylist=False, ltype='moovizon')

	def youtubeErr(self, error):
		print "youtubeErr: ",error
		self['handlung'].setText("Das Video kann leider nicht abgespielt werden !\n"+str(error))

	def keyCancel(self):
		self.close()