# -*- coding: latin-1 -*-

#Regex
RE_EP_NUM         = Regex('Épisode ([0-9]+)')

# Plugin parameters
PLUGIN_TITLE		= "TéléQuebec.tv"
PLUGIN_PREFIX   	= "/video/telequebec"
PLUGIN_URL		= "http://www.tou.tv/"

AZ_LIST="http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/Az"



MONTHS = [{"french" : "janvier", "english": "January"},{"french" : u"février", "english": "February"},{"french" : "mars", "english": "March"},
	{"french" : "avril", "english": "April"},{"french" : "mai", "english": "May"},{"french" : "juin", "english": "June"},
	{"french" : "juillet", "english": "July"},{"french" : u"août", "english": "August"},{"french" : "septembre", "english": "September"},
	{"french" : "octobre", "english": "October"},{"french" : "novembre", "english": "November"},{"french" : u"décembre", "english": "December"}]

####################################################################################################

def Start():
	#Set handler
	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE)
	
	# Set the default ObjectContainer attributes
	ObjectContainer.title1    = PLUGIN_TITLE

	# Set the default cache time
	HTTP.CacheTime = 1800
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'
	


###################################################################################################

def MainMenu():
	oc = ObjectContainer()
	
	oc.add(DirectoryObject(key=Callback(Carrousel), title="En Vedette"))
        oc.add(DirectoryObject(key=Callback(AllShows), title=u"Toutes les émissions"))
        oc.add(DirectoryObject(key=Callback(BrowseAlphabetically), title=u"Parcourir par ordre alphabétique"))
	
	return oc

####################################################################################################

def GetShowList():
	
	jsonRepertoire = JSON.ObjectFromURL(AZ_LIST)
	shows = jsonRepertoire["data"]["items"]
	
	return shows

####################################################################################################
@route(PLUGIN_PREFIX + '/Carrousel')

def Carrousel():
	oc = ObjectContainer(title2 ="En Vedette sur TOU.TV")
	
	jsonCarrousel = JSON.ObjectFromURL(CARROUSEL_SERVICE_URL)
	carrouselShows = jsonCarrousel["d"]
	shows = GetShowList()
	
	for carrouselShow in carrouselShows :
		showId = carrouselShow["EmissionId"]
		showTitle = carrouselShow["title"]
		showSubTitle = carrouselShow["subTitle"]
		showArt = carrouselShow["imgLR"]
		showThumb = carrouselShow["imgNR"]
		for show in shows :
			if show["Id"] == showId :
				oc.add(DirectoryObject(key=Callback(Show, show=show), title = showTitle, tagline = showSubTitle, summary = showSubTitle, thumb = Resource.ContentsOfURLWithFallback(url=showThumb), art = Resource.ContentsOfURLWithFallback(url=showArt)))
	
	
	return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/AllShows')

def AllShows():
	oc = ObjectContainer(title2 = u"Toutes les émissions")
	
	shows = GetShowList()
	for show in shows:
		try: 
			thumb = show["ImagePromoNormalK"]
		except:
			thumb = Resource.ContentsOfURLWithFallback(url=show["ImageJorC"])
		oc.add(DirectoryObject(key=Callback(Show, show=show), title = show["Titre"], thumb = thumb, art = Resource.ContentsOfURLWithFallback(url=show["ImageJorC"])))
	
	return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/BrowseGenre')

def BrowseByGenre():
	oc = ObjectContainer(title2 = "Parcourir par genre")
	
	jsonRepertoire = JSON.ObjectFromURL(REPERTOIRE_SERVICE_URL)
	genres = jsonRepertoire["d"]["Genres"]

	for genre in genres:
		oc.add(DirectoryObject(key=Callback(Genre, genre=genre), title=genre['Title'], art = Resource.ContentsOfURLWithFallback(url=genre["ImageBackground"])))
	
	return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/Genre', genre=list)

def Genre(genre):
	oc = ObjectContainer(title2 = genre['Title'])
	shows = GetShowList()
	for show in shows:
		if show['ParentId'] == genre['Id']:
			try: 
				thumb = show["ImagePromoNormalK"]
			except:
				thumb = Resource.ContentsOfURLWithFallback(url=show["ImageJorC"])
			oc.add(DirectoryObject(key=Callback(Show, show=show), title = show["Titre"], thumb = thumb, art = Resource.ContentsOfURLWithFallback(url=show["ImageJorC"])))

	
	return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/BrowseCountry')

def BrowseByCountry():
	oc = ObjectContainer(title2 = "Parcourir par pays")
	
	jsonRepertoire = JSON.ObjectFromURL(REPERTOIRE_SERVICE_URL)
	countries = jsonRepertoire["d"]["Pays"]
	
	
	for country in countries:
		oc.add(DirectoryObject(key=Callback(Country, country=country), title=country['Value']))
		#Would be cool to add flag icons for each country 
	return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/Country', country=list)

def Country(country):
	oc = ObjectContainer(title2 = country['Value'])
	shows = GetShowList()
	for show in shows : 
		if show['Pays'] == country['Value']:
			try: 
				thumb = show["ImagePromoNormalK"]
			except:
				thumb = Resource.ContentsOfURLWithFallback(url=show["ImageJorC"])
			oc.add(DirectoryObject(key=Callback(Show, show=show), title = show["Titre"], thumb = thumb, art = Resource.ContentsOfURLWithFallback(url=show["ImageJorC"])))

	return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/BrowseAlpha')

def BrowseAlphabetically():
	oc = ObjectContainer(title2 = u"Parcourir par ordre alphabétique")
	
	for letters in ["0-9", "ABC", "DEF", "GHI", "JKL", "MNO", "PQR", "STU", "VWXYZ"]:
		oc.add(DirectoryObject(key=Callback(Letters, letters=letters), title=letters))
		#would be cool to add thumbs with letters on R(icon)
	return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/Letters')

def Letters(letters):
	oc = ObjectContainer(title2 = letters)
	shows = GetShowList()
	if letters == "0-9":
		letters = "0123456789"
	index=0
	while index < len(letters):
		letter = letters[index]
		for show in shows:
			if show['Titre'].startswith(letter) : 
				try: 
					thumb = show["ImagePromoNormalK"]
				except:
					thumb = Resource.ContentsOfURLWithFallback(url=show["ImageJorC"])
				oc.add(DirectoryObject(key=Callback(Show, show=show), title = show["Titre"], thumb = thumb, art = Resource.ContentsOfURLWithFallback(url=show["ImageJorC"])))
		index = index + 1
	
	return oc
	
####################################################################################################
@route(PLUGIN_PREFIX + '/Show', show=list)

def Show(show):

	oc = ObjectContainer(title2 = show["Titre"])
	
	dataEmission = JSON.ObjectFromURL(EMISSION_SERVICE_URL + str(show["Id"]))
	jsonEmission = dataEmission["d"]["Emission"]
	jsonEpisodes = dataEmission["d"]["Episodes"]
	
	if jsonEpisodes[0]["IsUniqueEpisode"] == True :
		
		movieTitle = jsonEmission["Title"]
		movieSummary = jsonEpisodes[0]["Description"]
		#movieGenre = jsonEmission["Genre"]["Title"]
		movieYear = int(jsonEpisodes[0]["Year"])
		#movieTags = jsonEpisodes[0]["Keywords"].split(",")
		movieUrl= jsonEpisodes[0]["Url"]
		if not movieUrl.startswith(PLUGIN_URL):
			movieUrl = PLUGIN_URL + movieUrl.lstrip('/')
			
		movieDuration = int(jsonEpisodes[0]["Length"])
		try:
			movieThumb = jsonEpisodes[0]["ImageThumbMoyenL"]
		except:
			movieThumb = None
		try:
			movieArt = jsonEpisodes[0]["ImagePromoLargeL"]
		except:
			movieArt = None
			
		oc.add(MovieObject(url = movieUrl, title = movieTitle, summary = movieSummary, year = movieYear, duration = movieDuration, thumb = Resource.ContentsOfURLWithFallback(url = movieThumb), art = Resource.ContentsOfURLWithFallback(url=movieArt)))
                
	else:
		showId = show["Id"]
		try:
			seasonThumb = show["ImagePromoNormalK"]
		except:
			seasonThumb = None
					
		index = 0
		for season in show["NombreEpisodesParSaison"] :
			seasonTitle = "Saison " + str(season['Key'])
			oc.add(DirectoryObject(key=Callback(Season, show=show, showId=showId, index=index), title=seasonTitle, thumb=Resource.ContentsOfURLWithFallback(url=seasonThumb)))
			index = index + 1

	return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/Season', show=list, index=int)

def Season(show, showId, index):
	seasonTitle = "Saison " + str(show["NombreEpisodesParSaison"][index]['Key'])
	oc = ObjectContainer(title1 = show["Titre"], title2 = seasonTitle)

	episodes = JSON.ObjectFromURL(SEASON_INFO_URL % (showId, show["NombreEpisodesParSaison"][index]['Key']))
	for episode in episodes[0]['EpisodeVignetteList']:
		url=episode['DetailsViewUrl']
		if not url.startswith(PLUGIN_URL):
			url = PLUGIN_URL + url.lstrip('/')
		try:
			title = episode["DetailsViewTitre"] + " " + episode['EpisodeUrlEntity']['episode']
		except:
			title=episode['EpisodeUrlEntity']['episode']
		try:
			ep_index = int(RE_EP_NUM.search(episode['DetailsViewSaison']).group(1))
		except:
			ep_index = None

		#if title.startswith(u"épisode"):
			#if title.partition(':')[2] != '':
				#title = title.partition(':')[2].strip()	

		date = TranslateDate(episode['DetailsViewDateEpisode'])
		summary = episode['DetailsFullDescription']
		thumb = episode['DetailsViewImageUrlL'].replace('_L.jpeg','_A.jpeg')
		duration = Datetime.MillisecondsFromString(episode['DetailsViewDureeEpisode'])
		oc.add(EpisodeObject(url=url, title=title, show=show['Titre'], index=ep_index, originally_available_at=date, season=show["NombreEpisodesParSaison"][index]['Key'], summary=summary, thumb=Resource.ContentsOfURLWithFallback(url=thumb), art=Resource.ContentsOfURLWithFallback(url=thumb)))
	
	if len(oc) == 0:
		return ObjectContainer(header="Saison vide", message="Cette saison n'a aucun contenu.")
	
	return oc

####################################################################################################

def TranslateDate(date):
	for month in MONTHS:
		date = date.replace(month['french'], month['english'])
	return Datetime.ParseDate(date).date()

