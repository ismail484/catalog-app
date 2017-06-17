from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, MenuItem, User

engine = create_engine('sqlite:///catalogitemwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Mohamed Ismail", email="ghost9999100@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for Air sports
category1 = Category(user_id=1, name="AirSports")

session.add(category1)
session.commit()

menuItem1 = MenuItem(user_id=1, title="Aerobatics", description="Aerobatics are performed in airplanes and gliders for training, recreation, entertainment, and sport."
                     , category=category1)

session.add(menuItem1)
session.commit()


menuItem2 = MenuItem(user_id=1, title="Air racing", description=" is a motorsport that involves airplanes competing over a fixed course"
                     , category=category1)

session.add(menuItem2)
session.commit()



# Menu for Volleyball
category2 = Category(user_id=1, name="VolleyBall")

session.add(category2)
session.commit()


menuItem1 = MenuItem(user_id=1, title="Beach-Volleyball", description="Beach volleyball is a team sport played by two teams of two players on a sand court divided by a net"
                     , category=category2)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, title="Water-Volleyball ", description=" It is played in countries with a temperate or tropical climate and less frequently in cold climates"
                     , category=category2)

session.add(menuItem2)
session.commit()

menuItem3 = MenuItem(user_id=1, title="Sitting-Volleyball", description=" Sitting volleyball (sometimes known as paralympic volleyball) is a form of volleyball for athletes with a disability that entered the Paralympic Games "
                     , category=category2)

session.add(menuItem3)
session.commit()



# Menu for BasketballFamily
category3 = Category(user_id=1, name="BasketballFamily")

session.add(category3)
session.commit()


menuItem1 = MenuItem(user_id=1, title="Beach-Basketball", description="Beach Basketball is a modified version of basketball, played on beaches. It was invented in the United States by Philip Bryant"
                     , category=category3)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, title="Deaf-Basketball", description="Deaf basketball is basketball played by deaf people. Sign language is used to communicate whistle blows and communication between players"
                     , category=category3)

session.add(menuItem2)
session.commit()



# Menu for Softball
category4 = Category(user_id=1, name="SoftBall")

session.add(category4)
session.commit()


menuItem1 = MenuItem(user_id=1, title="Fastpitch-Softball", description="it is a form of softball played commonly by women and men"
                     , category=category4)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, title="16-inch-Softball", description="it is a variant of softball, but using a bigger, squishier ball with no gloves or mitts on the fielders"
                     , category=category4)

session.add(menuItem2)
session.commit()

# Menu for Cycling
category5 = Category(user_id=1, name="Cycling")

session.add(category5)
session.commit()


menuItem1 = MenuItem(user_id=1, title="Bicycle", description="A bicycle, also called a cycle or bike, is a human-powered, pedal-driven, single-track vehicle, having two wheels attached to a frame"
                     , category=category5)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, title="Skibobbing", description="Skibobbing is a winter sport involving a bicycle-type frame attached to skis instead of wheels and a set of foot skis"
                     , category=category5)

session.add(menuItem2)
session.commit()


# Menu for SnowSports
category6 = Category(user_id=1, name="SnowSports")

session.add(category6)
session.commit()


menuItem1 = MenuItem(user_id=1, title="Skiing", description="This article is about snow skiing. For water skiing, see Waterskiing. For other uses, see Skiing (disambiguation)."
                     , category=category6)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, title="Sledding", description="Sledding, sledging or tobogganing is a worldwide winter activity, generally carried out in a prone or seated position"
                     , category=category6)

session.add(menuItem2)
session.commit()


# Menu for Aquatic ball sports
category7 = Category(user_id=1, name="AquaticBallSports")

session.add(category7)
session.commit()


menuItem1 = MenuItem(user_id=1, title="WaterPolo", description="Water polo is a competitive team sport played in the water between two teams"
                     , category=category7)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, title="CanoePolo", description="Canoe polo, also known as Kayak polo, is one of the competitive disciplines of canoeing, known simply  by its aficionados"
                     , category=category7)

session.add(menuItem2)
session.commit()


# Menu for 	Motorized sports
category8 = Category(user_id=1, name="MotorizedSports")

session.add(category8)
session.commit()


menuItem1 = MenuItem(user_id=1, title="AutoRacing", description="is a sport involving the racing of automobiles for competition"
                     , category=category8)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, title="MotorboatRacing", description=" is a type of racing by ocean-going powerboats, typically point-to-point racing."
                     , category=category8)

session.add(menuItem2)
session.commit()


# Menu for 	Mind sports
category9 = Category(user_id=1, name="MindSports")

session.add(category9)
session.commit()


menuItem1 = MenuItem(user_id=1, title="CardGames", description="A card game is any game using playing cards as the primary device with which the game is played"
                     , category=category9)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, title="SpeedCubing", description=" Speedcubing (also known as speedsolving) is the activity of solving a variety of twisty puzzles,"
                     , category=category9)

session.add(menuItem2)
session.commit()


# Menu for 	StickGames
category10 = Category(user_id=1, name="StickGames")

session.add(category10)
session.commit()


menuItem1 = MenuItem(user_id=1, title="Hockey", description="Hockey is a sport in which two teams play against each other by trying to maneuver a ball or a puck into the opponent's goal "
                     , category=category10)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, title="Broomball", description=" Broomball is a recreational ice game originating in Canada (also contested as being Swedish) and played in certain other countries,"
                     , category=category10)

session.add(menuItem2)
session.commit()



print "added menu items!"
