import json
from player import Player
import xml.etree.ElementTree as ET
from player_pb2 import PlayersList, Class


class PlayerFactory:
    def to_json(self, players):
        returned_json = []
        for player in players:
            new_player = {
                "nickname": player.nickname,
                "email": player.email,
                "date_of_birth": player.date_of_birth.strftime("%Y-%m-%d"),
                "xp": player.xp,
                "class": player.cls
            }
            returned_json.append(new_player)
        return returned_json

    def from_json(self, list_of_dict):
        players = []
        for dict in list_of_dict:
            new_player = Player(dict['nickname'], dict['email'], dict['date_of_birth'], int(
                dict['xp']), dict['class'])
            players.append(new_player)
        return players

    def to_xml(self, list_of_players):

        usrconfig = ET.Element("usrconfig")
        usrconfig = ET.SubElement(usrconfig, "data")
        for player in list_of_players:
            usr = ET.SubElement(usrconfig, "player")

            nick = ET.SubElement(usr, "nickname")
            nick.text = player.nickname

            email = ET.SubElement(usr, "email")
            email.text = player.email

            date_of_birth = ET.SubElement(usr, "date_of_birth")
            date_of_birth.text = player.date_of_birth.strftime("%Y-%m-%d")

            xp = ET.SubElement(usr, "xp")
            xp.text = str(player.xp)

            clss = ET.SubElement(usr, "class")
            clss.text = player.cls

        return ET.tostring(usrconfig, encoding='utf8')

    def from_xml(self, xml_string):
        root = ET.fromstring(xml_string)
        players = []
        for child in root:
            list = []
            for secondary in child:
                list.append(secondary.text)
            players.append(
                Player(list[0], list[1], list[2], int(list[3]), list[4]))
        return players

    def from_protobuf(self, binary):
        players_list_proto = PlayersList()
        players_list_proto.ParseFromString(binary)

        players = []

        for player_proto in players_list_proto.player:
            date_str = player_proto.date_of_birth
            class_str = Class.Name(player_proto.cls)
            player = Player(player_proto.nickname, player_proto.email, date_str, player_proto.xp, class_str)
            players.append(player)

        return players

    def to_protobuf(self, list_of_players):
        players_list_proto = PlayersList()

        for player in list_of_players:
            player_proto = players_list_proto.player.add()
            player_proto.nickname = player.nickname
            player_proto.email = player.email
            player_proto.date_of_birth = player.date_of_birth.strftime("%Y-%m-%d")
            player_proto.xp = player.xp

            if player.cls == "Berserk":
                player_proto.cls = Class.Berserk
            elif player.cls == "Tank":
                player_proto.cls = Class.Tank
            elif player.cls == "Paladin":
                player_proto.cls = Class.Paladin
            elif player.cls == "Mage":
                player_proto.cls = Class.Mage
            else:
                raise ValueError("Invalid player class: " + player.cls)

        return players_list_proto.SerializeToString()

