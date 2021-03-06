from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from datetime import date,datetime
from parladata.models import *
from django.forms.models import model_to_dict
import json, simplejson
from utils import *
import requests


'''
MP = Members of parlament
#Function: git config
'''
def getMPs(request):
	data = []
	parliamentary_group = Organization.objects.filter(classification="poslanska skupina")
	for i in getMPObjects():
		district = ''

		if i.district != None:
			district = i.district.name

		membership = Membership.objects.filter(person = i, organization=parliamentary_group)
		data.append({'id': i.id, 'name':i.name,'membership':membership[0].organization.name, 'acronym':membership[0].organization.acronym,'classification':i.classification,'family_name':i.family_name,'given_name':i.given_name,'additional_name':i.additional_name,'honorific_prefix':i.honorific_prefix,'honorific_suffix':i.honorific_suffix,'patronymic_name':i.patronymic_name,'sort_name':i.sort_name,'email':i.email,'gender':i.gender,'birth_date':str(i.birth_date),'death_date':str(i.death_date),'summary':i.summary,'biography':i.biography,'image':i.image,'district':'','gov_url':i.gov_url.url,'gov_id':i.gov_id,'gov_picture_url':i.gov_picture_url,'voters':i.voters,'active':i.active})
	return  JsonResponse(data, safe=False)

#returns MP static data like PoliticalParty, age, ....
def getMPStatic(request, person_id):
    data = dict()
    for member in getMPObjects():
        if str(member.id) == str(person_id):

            groups = [{'name': membership.organization.name, 'id': membership.organization.id, 'acronym': membership.organization.acronym} for membership in member.memberships.all() if membership.organization.classification == u'poslanska skupina']

            non_party_groups = [{'name': membership.organization.name, 'id': membership.organization.id} for membership in member.memberships.all() if membership.organization.classification != u'poslanska skupina']

            for group in non_party_groups:
                groups.append(group)

            print groups

            birth_date = str(member.birth_date)
            #creates a list of all memberships of MP
#            for i in parliamentary_group:
#                groups.append(i.organization)
            #calcutaes age of MP
            age = date.today() - date(int(birth_date[:4]),int(birth_date[5:7]),int(birth_date[8:10]))
            age = age.days / 365

            twitter = member.link_set.filter(tags__name__in=['twitter'])
            facebook = member.link_set.filter(tags__name__in=['facebook'])
            linkedin = member.link_set.filter(tags__name__in=['linkedin'])

            social_output = {}
            if len(twitter) > 0:
                social_output['twitter'] = twitter[0].url
            else:
                social_output['twitter'] = False
            if len(facebook) > 0:
                social_output['facebook'] = facebook[0].url
            else:
                social_output['facebook'] = False
            if len(linkedin) > 0:
                social_output['linkedin'] = linkedin[0].url
            else:
                social_output['linkedin'] = False

            district = member.district.name if member.district else None

            data = {
                'previous_occupation': member.previous_occupation,
                'education': member.education,
                'mandates': member.mandates,
                'party': groups[0]['name'],
                'acronym': groups[0]['acronym'],
                'party_id': groups[0]['id'],
                'district': district,
                'voters': member.voters,
                'age': age,
                'groups': [{'name': group['name'], 'id': group['id']} for group in groups[1:]],
                'name': member.name,
                'social': social_output
            }

    return JsonResponse(data)

#return all Sessions
def getSessions(request):
    data = []
    sessions = Session.objects.all()
    for i in sessions:
        data.append({'mandate': i.mandate,
                     'name': i.name,
                     'gov_id': i.gov_id,
                     'start_time': i.start_time,
                     'end_time': i.end_time,
                     'organization': i.organization.name,
                     'classification': i.classification,
                     'id': i.id
                    })
    return JsonResponse(data, safe=False)

#return votes of MP
def getVotes(request):
	return JsonResponse(getVotesDict())

#return speech by id
def getSpeeches(request, person_id):

    speaker_list = Person.objects.filter(id=person_id)
    if len(speaker_list) > 0:
        speaker = speaker_list[0]

	speeches_queryset = Speech.objects.filter(speaker=speaker)

    speeches = [{'content': speech.content, 'speech_id': speech.id} for speech in speeches_queryset]

    return JsonResponse(speeches, safe=False)

'''
PG = Parlamentary group

return list of member's id for each PG
'''
def getMembersOfPGs(request):
	parliamentary_group = Organization.objects.filter(classification="poslanska skupina")
	members = Membership.objects.filter(organization__in=parliamentary_group)
	data = {pg.id:[member.person.id for member in members.filter(organization=pg)] for pg in parliamentary_group}
	return JsonResponse(data)



#get coalitions PGs
def getCoalitionPGs(request):
	coalition = Organization.objects.filter(classification="poslanska skupina", is_coalition="1").values_list("id", flat=True)
	return JsonResponse({'coalition':list(coalition)})

#return number of MP attended sessions
def getNumberOfMPAttendedSessions(request, person_id):
	data = {}
	allBallots = Ballot.objects.filter(option='za')
	for i in getMPObjects():
		data[i.id] = len(list(set(allBallots.filter(voter=i.id).values_list('vote__session', flat=True))))
	return JsonResponse(data[int(person_id)], safe=False)

def getNumberOfAllMPAttendedSessions(request):
	data = {}
	allBallots = Ballot.objects.filter(option='za')
	for i in getMPObjects():
		data[i.id] = len(list(set(allBallots.filter(voter=i.id).values_list('vote__session', flat=True))))
	return JsonResponse(data)

#return all speeches of all MP
def getSpeechesOfMP(request, person_id):
	content = {}
	for i in getMPObjects():
		content[i.id] = list(Speech.objects.filter(speaker__id = i.id).values_list('content', flat=True))
	return JsonResponse(content[int(person_id)], safe=False)

def getAllSpeeches(request):

    speeches_queryset = Speech.objects.all()

    speeches = [{'content': speech.content, 'speech_id': speech.id, 'speaker':speech.speaker.id, 'session_name':speech.session.name, 'session_id':speech.session.id,} for speech in speeches_queryset]

    return JsonResponse(speeches, safe=False)

def getMPParty(request, person_id):
    person = Person.objects.get(id=person_id)

    parties = [{'name': membership.organization.name, 'id': membership.organization.id, 'acronym': membership.organization.acronym} for membership in person.memberships.all() if membership.organization.classification == u'poslanska skupina']

    out = {'name': parties[0]['name'], 'id': parties[0]['id'], 'acronym': parties[0]['acronym']}

    return JsonResponse(out)

#returns number of seats in each parliamentary group
def getNumberOfSeatsOfPG(request, pg_id):
    value = dict()
    parliamentary_group = Organization.objects.filter(classification="poslanska skupina",id = int(pg_id))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    data = {pg.id:len([member.person.id for member in members.filter(organization=pg)]) for pg in parliamentary_group}
    value = {int(pg_id):data[int(pg_id)]}
    return JsonResponse(value, safe=False)


#return basic info of parlament group
def getBasicInfOfPG(request, pg_id):
    data = dict()
    listOfVotes = []
    parliamentary_group = Organization.objects.filter(classification="poslanska skupina", id=int(pg_id))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    headOfPG = Membership.objects.filter(role="vodja", organization__in=parliamentary_group)[0].person.id
    #viceOfPG = Membership.objects.filter(role="namestnik", organization__in=parliamentary_group)[0].person.name
    numberOfSeats = len(members)
    for a in members:
        listOfVotes.append(a.person.voters)
    #allVoters = sum(listOfVotes)
    FB = Link.objects.filter(organization = parliamentary_group, note = 'facebook')
    mail  = Link.objects.filter(organization = parliamentary_group, note = 'mail')
    twitter = Link.objects.filter(organization = parliamentary_group, note = 'twitter')
    data = {
    "HeadOfPG":headOfPG,
    #"ViceOfPG":viceOfPG,
    "NumberOfSeats":numberOfSeats,
    #"AllVoters":allVoters,
    #"Mail":mail,
    #"Facebook":FB,
    #"Twitter":twitter
    }
    return JsonResponse(data, safe=False)

def getAllPGs(request):
    parliamentary_group = Organization.objects.filter(classification="poslanska skupina")
    data = {pg.id:pg.name for pg in parliamentary_group}
    return JsonResponse(data)

def getAllOrganizations(requests):
    org = Organization.objects.all()
    data = {pg.id:{'name':pg.name,'classification':pg.classification} for pg in org}
    return JsonResponse(data)


def getAllSpeeches(requests):
    data = []

    speeches=Speech.objects.all()
    for speech in speeches:
        data.append(model_to_dict(speech, fields=[field.name for field in speech._meta.fields], exclude=[]))

    return JsonResponse(data, safe=False)


def getAllVotes(requests):
    data = []

    votes=Vote.objects.all()
    for vote in votes:
        data.append({'id': vote.id, 'motion': vote.motion.text, 'party': vote.organization.id, 'session': vote.session.id, 'start_time': vote.start_time, 'end_time': vote.end_time, 'result': vote.result})

    return JsonResponse(data, safe=False)


def getAllBallots(requests):
    data = []

    ballots = Ballot.objects.all()
    
#    data = [{'id': ballot.id, 'vote': ballot.vote.id, 'voter': ballot.voter.id, 'option': ballot.option, 'time': ballot.vote.start_time} for ballot in ballots]
    
    for ballot in ballots:
#        data.append({'id': ballot.id, 'vote': ballot.vote.id, 'voter': ballot.voter.id, 'option': ballot.option, 'time': ballot.vote.start_time})
        interimdata = model_to_dict(ballot, fields=['id', 'vote', 'voter', 'option'], exclude=[])
        
#        time = ballot.vote.start_time
#        interimdata['time'] = time
        
        data.append(interimdata)

    return JsonResponse(data, safe=False)


def getAllPeople(requests):
    parliamentary_group = Organization.objects.filter(classification="poslanska skupina")
    data = []
    pg=''
    person = Person.objects.all()
    for i in person:
        membership = Membership.objects.filter(person = i.id, organization=parliamentary_group)
        for me in membership:
            pg = me.organization.name
        data.append({'id': i.id, 'name':i.name, 'membership':pg, 'classification':i.classification,'family_name':i.family_name,'given_name':i.given_name,'additional_name':i.additional_name,'honorific_prefix':i.honorific_prefix,'honorific_suffix':i.honorific_suffix,'patronymic_name':i.patronymic_name,'sort_name':i.sort_name,'email':i.email,'gender':i.gender,'birth_date':str(i.birth_date),'death_date':str(i.death_date),'summary':i.summary,'biography':i.biography,'image':i.image,'district':'','gov_id':i.gov_id,'gov_picture_url':i.gov_picture_url,'voters':i.voters,'active':i.active})
        pg=None
    return  JsonResponse(data, safe=False)
