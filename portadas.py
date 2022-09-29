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
        color: str='white'
    ) -> None:
    
        self.facebook = facebook
        self.twitter = twitter
        self.name = name
        self.sm = sm
        self.x = x
        self.y = y
        self.size = size
        self.color = color

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
            name='Fnatic',
            x={'Facebook': 510, 'Twitter': 950},
            y={'Facebook': 185, 'Twitter': 250},
            size={'Facebook': 30, 'Twitter': 42},
        )

        self.isurus = Team(
            facebook='https://static.wixstatic.com/media/3c06e6_608acbe2ed8e42428c3344646d346f89~mv2.png', 
            twitter='https://static.wixstatic.com/media/3c06e6_525720d4f5c84eaea6e397e2a82d93ac~mv2.png',
            name='Isurus',
            x={'Facebook': 550, 'Twitter': 1153},
            y={'Facebook': 185, 'Twitter': 250},
            size={'Facebook': 14, 'Twitter': 24},
            color='#0e3857'
        )

    # mad_lions = team(facebook=, twitter=)
    # g2 = team(facebook=, twitter=)
    # t1 = team(facebook=, twitter=)
    # c9 = team(facebook=, twitter=)
    # loud = team(facebook=, twitter=)

    def return_team(self, team):        
        match team:
            case self.fnatic.name:
                return self.fnatic
            case self.isurus.name:
                return self.isurus
            case _:
                return 0

portadas = Portadas()