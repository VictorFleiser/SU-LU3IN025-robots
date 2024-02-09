# Projet "robotique" IA&Jeux 2023
#
# Binome:
#  Prénom Nom: Victor Fleiser
#  Prénom Nom: Thomas Marchand

from random import choice
import math

def get_team_name():
    return "MaRoomba & LuigIA"

var_robots = [0 for _ in range(8)]  #variable de chaque robot

def step(robotId, sensors):

    #valeurs par défaut
    translation = 0 # vitesse de translation (entre -1 et +1)
    rotation = 0 # vitesse de rotation (entre -1 et +1)

    def get_sensor_values(sensors) :
        #retourne un dictionaire des valeurs des sensors plus spécifiques, pour rendre les tests moins verbaux
        #pour chaque sensor, donne la distance si c'est un robot alié, si c'est un robot ennemi, si c'est un mur, si c'est un robot, et la distance de base. Et plus encore de valeurs

        sensor_values = {}
        sensors_list = ["front", "front_left", "front_right", "left", "right", "back_left", "back_right", "back"]
        for sensor in sensors_list :
            sensor_values.update({sensor : (sensors["sensor_" + sensor]["distance"])})
            sensor_values.update({sensor + "_robot" : (sensors["sensor_" + sensor]["distance"] if (sensors["sensor_" + sensor]["isRobot"]) else 1)})
            sensor_values.update({sensor + "_ally" : (sensors["sensor_" + sensor]["distance"] if (sensors["sensor_" + sensor]["isRobot"] and sensors["sensor_" + sensor]["isSameTeam"]) else 1)}) 
            sensor_values.update({sensor + "_enemy" : (sensors["sensor_" + sensor]["distance"] if (sensors["sensor_" + sensor]["isRobot"] and not sensors["sensor_" + sensor]["isSameTeam"]) else 1)}) 
            sensor_values.update({sensor + "_wall" : (sensors["sensor_" + sensor]["distance"] if (not sensors["sensor_" + sensor]["isRobot"]) else 1)})
        
        #distance minimum pour tous les sensors
        sensor_values.update({"all" : (min(sensor_values["front"], sensor_values["front_left"], sensor_values["front_right"], sensor_values["left"], sensor_values["right"], sensor_values["back_left"], sensor_values["back_right"], sensor_values["back"]))})
        sensor_values.update({"all_robot" : (min(sensor_values["front_robot"], sensor_values["front_left_robot"], sensor_values["front_right_robot"], sensor_values["left_robot"], sensor_values["right_robot"], sensor_values["back_left_robot"], sensor_values["back_right_robot"], sensor_values["back_robot"]))})
        sensor_values.update({"all_ally" : (min(sensor_values["front_ally"], sensor_values["front_left_ally"], sensor_values["front_right_ally"], sensor_values["left_ally"], sensor_values["right_ally"], sensor_values["back_left_ally"], sensor_values["back_right_ally"], sensor_values["back_ally"]))})
        sensor_values.update({"all_enemy" : (min(sensor_values["front_enemy"], sensor_values["front_left_enemy"], sensor_values["front_right_enemy"], sensor_values["left_enemy"], sensor_values["right_enemy"], sensor_values["back_left_enemy"], sensor_values["back_right_enemy"], sensor_values["back_enemy"]))})
        sensor_values.update({"all_wall" : (min(sensor_values["front_wall"], sensor_values["front_left_wall"], sensor_values["front_right_wall"], sensor_values["left_wall"], sensor_values["right_wall"], sensor_values["back_left_wall"], sensor_values["back_right_wall"], sensor_values["back_wall"]))})
        
        #distance minimum pour tous les sensors devant (left, front_left, front, front_right, right)
        sensor_values.update({"all_front" : (min(sensor_values["front"], sensor_values["front_left"], sensor_values["front_right"], sensor_values["left"], sensor_values["right"]))})
        sensor_values.update({"all_robot_front" : (min(sensor_values["front_robot"], sensor_values["front_left_robot"], sensor_values["front_right_robot"], sensor_values["left_robot"], sensor_values["right_robot"]))})
        sensor_values.update({"all_ally_front" : (min(sensor_values["front_ally"], sensor_values["front_left_ally"], sensor_values["front_right_ally"], sensor_values["left_ally"], sensor_values["right_ally"]))})
        sensor_values.update({"all_enemy_front" : (min(sensor_values["front_enemy"], sensor_values["front_left_enemy"], sensor_values["front_right_enemy"], sensor_values["left_enemy"], sensor_values["right_enemy"]))})
        sensor_values.update({"all_wall_front" : (min(sensor_values["front_wall"], sensor_values["front_left_wall"], sensor_values["front_right_wall"], sensor_values["left_wall"], sensor_values["right_wall"]))})

        #distance minimum pour tous les sensors derriere (back_left, back, back_right)
        sensor_values.update({"all_back" : (min(sensor_values["back"], sensor_values["back_left"], sensor_values["back_right"]))})
        sensor_values.update({"all_robot_back" : (min(sensor_values["back_robot"], sensor_values["back_left_robot"], sensor_values["back_right_robot"]))})
        sensor_values.update({"all_ally_back" : (min(sensor_values["back_ally"], sensor_values["back_left_ally"], sensor_values["back_right_ally"]))})
        sensor_values.update({"all_enemy_back" : (min(sensor_values["back_enemy"], sensor_values["back_left_enemy"], sensor_values["back_right_enemy"]))})
        sensor_values.update({"all_wall_back" : (min(sensor_values["back_wall"], sensor_values["back_left_wall"], sensor_values["back_right_wall"]))})

        #distance minimum pour les sensors de suiveur de murs gauche (left, front_left,front)
        sensor_values.update({"all_wall_front_left" : (min(sensor_values["left_wall"], sensor_values["front_left_wall"], sensor_values["front_wall"]))})
        #distance minimum pour les sensors de suiveur de murs droite (right, front_right,front)
        sensor_values.update({"all_wall_front_right" : (min(sensor_values["right_wall"], sensor_values["front_right_wall"], sensor_values["front_wall"]))})

        return sensor_values
        
    def FollowWallBot(sv, robotId, wall = "left"):
        #strategie suiveur de mur (gauche ou droite), attention : si pas à coté d'un mur, il va tourner dans le vide

        rotation = 0
        translation = 1

        #weights :
        rotation_weights = {}
        #weights pour suivre les murs à gauche :
        rotation_weights.update({"left_wall" : -1, "front_left_wall" : -1})
        #weights pour suivre les murs à droite :
        rotation_weights.update({"right_wall" : 1, "front_right_wall" : 1})
        #weight pour front_wall dépend du mur ) suivre
        if (wall == "left") :
            rotation_weights.update({"front_wall" : 10})
        else :
            rotation_weights.update({"front_wall" : -10})

        if (wall == "left") :
            rotation += rotation_weights["front_wall"] * (1 - sv["front_wall"]) + rotation_weights["left_wall"] * (sv["left_wall"] - 0.4375) + rotation_weights["front_left_wall"]  * (sv["front_left_wall"] - 0.8125) #+ (1) * (sv["back_left_wall"] - 0.8125)
            #print(rotation_weights["front_wall"], "*", (1 - sv["front_wall"]), "+", rotation_weights["left_wall"], "*", (sv["left_wall"] - 0.4375), "+", rotation_weights["front_left_wall"], "*", (sv["front_left_wall"] - 0.8125), "=", rotation)
        elif (wall == "right") :
            rotation += rotation_weights["front_wall"]  * (1 - sv["front_wall"]) + rotation_weights["right_wall"]  * (sv["right_wall"] - 0.4375) + rotation_weights["front_right_wall"]  * (sv["front_right_wall"] - 0.8125) #+ (-1) * (sv["back_right_wall"] - 0.8125)
        else :
            raise ValueError('followWallsBot : argument wall incorrect.')
        
        rotation += (choice([0.1, -0.1])) * (1-sv["all"])
        return (translation, rotation)

    def loverBot(sv) :
        #loveBot suit les robots ennemis mais reste fidèle à son amour et évite les robots alliés

        translation = 1

        #weights pour suivre l'ennemi :
        rotation_weights = {"left_enemy" : 1, "front_left_enemy" : 1, "front_right_enemy" : -1, "right_enemy" : -1, "back_right_enemy" : -1, "back_left_enemy" : 1} #, "back_enemy" : 1
        #weights pour éviter les murs :
        rotation_weights.update({"left_wall" : -1, "front_left_wall" : -1, "front_right_wall" : 1, "right_wall" : 1})   #"back_right_wall" : -1, "back_left_wall" : 1
        #weights pour éviter les alliés :
        rotation_weights.update({"left_ally" : -10, "front_left_ally" : -10, "front_right_ally" : 10, "right_ally" : 10, "back_left_ally" : -10, "back_right_ally" : 10})

        #Calcul de Braitenberg pour la rotation :
        rotation = 0
        for sensor_value in rotation_weights.keys():
            rotation += rotation_weights[sensor_value] * sv[sensor_value]

        #small rotation if stuck
        rotation += (choice([0.1, -0.1])) * (1-sv["all"])

        #détecte si il y a un ennemis directement derrière
        if (sv["back_enemy"] != 1) :
            rotation += (choice([1, -1]))

        return (translation, rotation)

    def randomBot(random_rotation = lambda: choice([1, -1]), random_translation = -1) :
        # fait des moves aléatoires : utile pour débloquer un softlock de temps à autres
        # random_rotation est le lambda pour déterminer la rotation aléatoire

        translation = random_translation
        rotation = random_rotation
        return (translation, rotation)
    
    def turnAroundBot(robotId, direction):
        #tourne au départ sur lui même pour suivre le mur arrière

        return (0, (-1 if direction == "left" else 1))

    def diagStartBot(robotId, direction, rotation = 0.75):
        #tourne en diagonal au départ

        return (1, (-rotation if direction == "left" else rotation))

    def maRoomba(sv, robotId, random = False, diag = False, wall = "left", turnAroundAtStart = False, rotation=0.75) :
        #possède un comportement customizable avec les paramètres, sinon essaie de suivre les ennemis et fuir les alliés, sinon suit un mur

        #augmentation de la clock du robot
        global var_robots
        var_robots[robotId] += 1 

        if (diag) :
            if (var_robots[robotId] <= 2) :
                return diagStartBot(robotId, wall, rotation)
        if (random) :
            if (var_robots[robotId]%400 > 393) :
                return randomBot(-1)
        if (turnAroundAtStart) :
            if (var_robots[robotId] <= 3) :
                return turnAroundBot(robotId, wall)

        if sv["all_robot"] < 1:
            translation, rotation = loverBot(sv)
        else :
            if (sv["all_wall_front_" + wall] < 1) :
                translation, rotation = FollowWallBot(sv, robotId, wall)
            else :
                translation, rotation = loverBot(sv)    #wanderBot()
        
        return (translation, rotation)

    def luigIA(sv) :
        if sv["all_robot"] < 1:
           return loverBot(sv)
        else :
            #Braitenberg issus d'évolution génétique

            # paramètres affinés par évolution génétique
            param = [0.1, -0.77, -0.92, 0.54, -0.39, -0.57, -0.09, -0.45, -0.14, -0.33, -0.82, 0.11, -0.41, -0.7, 0.06]
        
            rotation = math.tanh ( param[0] * (1-sv["left_wall"]) + param[1] * (1-sv["left_ally"]) + param[2] * (1-sv["left_enemy"]) + param[3] * (1-sv["front_left_wall"]) + param[4] * (1-sv["front_left_ally"]) + param[5] * (1-sv["front_left_enemy"]) + param[6] * (1-sv["front_wall"]) + param[7] * (1-sv["front_ally"]) + param[8] * (1-sv["front_enemy"]) + param[9] * (1-sv["front_right_wall"]) + param[10] * (1-sv["front_right_ally"]) + param[11] * (1-sv["front_right_enemy"]) + param[12] * (1-sv["right_wall"]) + param[13] * (1-sv["right_ally"]) + param[14] * (1-sv["right_enemy"]) )
            return (1, rotation)

    # def luigIA(sv) :
    #     #Braitenberg issus d'évolution génétique

    #     # paramètres affinés par évolution génétique
    #     param = [0.1, -0.77, -0.92, 0.54, -0.39, -0.57, -0.09, -0.45, -0.14, -0.33, -0.82, 0.11, -0.41, -0.7, 0.06]
    
    #     rotation = math.tanh ( param[0] * (1-sv["left_wall"]) + param[1] * (1-sv["left_ally"]) + param[2] * (1-sv["left_enemy"]) + param[3] * (1-sv["front_left_wall"]) + param[4] * (1-sv["front_left_ally"]) + param[5] * (1-sv["front_left_enemy"]) + param[6] * (1-sv["front_wall"]) + param[7] * (1-sv["front_ally"]) + param[8] * (1-sv["front_enemy"]) + param[9] * (1-sv["front_right_wall"]) + param[10] * (1-sv["front_right_ally"]) + param[11] * (1-sv["front_right_enemy"]) + param[12] * (1-sv["right_wall"]) + param[13] * (1-sv["right_ally"]) + param[14] * (1-sv["right_enemy"]) )
    #     return (1, rotation)

    sv = get_sensor_values(sensors)

    match robotId :
        case 0 :
            translation, rotation = luigIA(sv)
        case 1 :
            translation, rotation = maRoomba(sv, int(robotId), random=True, diag=False, wall="right", turnAroundAtStart=False, rotation=0.75)
        case 2 :
            translation, rotation = luigIA(sv)
        case 3 :
            translation, rotation = maRoomba(sv, int(robotId), random=True, diag=False, wall="right", turnAroundAtStart=False, rotation=0.75)
        case 4 :
            translation, rotation = maRoomba(sv, int(robotId), random=True, diag=False, wall="right", turnAroundAtStart=False, rotation=0.75)
        case 5 :
            translation, rotation = luigIA(sv)
        case 6 :
            translation, rotation = maRoomba(sv, int(robotId), random=True, diag=False, wall="right", turnAroundAtStart=False, rotation=0.75)
        case 7 :
            translation, rotation = luigIA(sv)
    return translation, rotation 
