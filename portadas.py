from PIL import Image, ImageFont, ImageDraw
from urllib.request import urlopen
import io

class Team():
    def __init__(
        self,
        facebook: str=None,
        twitter: str=None,
        name: str=None,
        sm: str=None,
        x: int=None,
        y: int=None,
        size: int=None,
        color: str='white',
        frame: str=None,
        anchor: str='rm'
    ) -> None:
    
        self.facebook = facebook
        self.twitter = twitter
        self.name = name
        self.sm = sm
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.frame = frame
        self.anchor = anchor

    def return_social_media_link(self, sm):    
        if sm == 'Facebook':
            return self.facebook
        else:
            return self.twitter

class Portadas():
    def __init__(self, team: str=None, ssmm: str=None) -> None:
        self.team = team
        self.ssmm = ssmm

        self.fnatic = Team(
            facebook='https://static.wixstatic.com/media/3c06e6_55e4d4b7c51f44668a11119f6407e41d~mv2.png', 
            twitter='https://static.wixstatic.com/media/3c06e6_2b2bd01f110d432f9ed5a1c8bda2cdb1~mv2.png',
            frame='https://static.wixstatic.com/media/3c06e6_4dbb3dccb06241ac934de7e533419058~mv2.png',
            name='Fnatic',
            x={'Facebook': 510, 'Twitter': 950},
            y={'Facebook': 185, 'Twitter': 250},
            size={'Facebook': 30, 'Twitter': 42},
        )

        self.isurus = Team(
            facebook='https://static.wixstatic.com/media/3c06e6_608acbe2ed8e42428c3344646d346f89~mv2.png', 
            twitter='https://static.wixstatic.com/media/3c06e6_525720d4f5c84eaea6e397e2a82d93ac~mv2.png',
            frame='https://static.wixstatic.com/media/3c06e6_e686e67c17d94ebb874be3f7d0469e99~mv2.png',
            name='Isurus',
            x={'Facebook': 550, 'Twitter': 1153},
            y={'Facebook': 185, 'Twitter': 250},
            size={'Facebook': 14, 'Twitter': 24},
            color='#0e3857',
        )

        self.t1 = Team(
            facebook='https://static.wixstatic.com/media/66910b_ba6354b8e49e4b3286e1ff50d7f17124~mv2.png',
            twitter='https://static.wixstatic.com/media/66910b_773bf3367e33432d9520f24c3c77c50b~mv2.png',
            name='T1',
            x={'Facebook': 420, 'Twitter': 670},
            y={'Facebook': 180, 'Twitter': 250},
            size={'Facebook': 18, 'Twitter': 26},
            color='white',
            anchor='lm'
        )

    # mad_lions = team(facebook=, twitter=)
    # g2 = team(facebook=, twitter=)
    # c9 = team(facebook=, twitter=)
    # loud = team(facebook=, twitter=)
    def return_team(self, team):        
        match team:
            case self.fnatic.name:
                return self.fnatic
            case self.isurus.name:
                return self.isurus
            case self.t1.name:
                return self.t1
            case _:
                return 0

portadas = Portadas()