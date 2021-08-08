# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 18:19:14 2020

@author: 17207
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 16:15:34 2020

@author: karan
"""
import pygame as pg
import random
import numpy as np
import pickle
pg.init()
running = True

#window size
width = 200
height = 200
screen = pg.display.set_mode((width,height))

#initializing images
carimg = pg.image.load('car.png')
car_shape = (16,16)
rockimg = pg.image.load('barrier.png')
rock_shape = (16,16)
finishimg = pg.image.load('finish-line.png')
finish_shape = (16,16)
#print(car_shape,rock_shape,finish_shape)
#positions
car_pos = (20,180)
rock1_pos = (35,40)
rock1_xrange = np.arange(rock1_pos[0]-15,rock1_pos[0]+16) 
rock1_yrange = np.arange(rock1_pos[1]-15,rock1_pos[1]+16)
rock2_pos = (170,170)
rock2_xrange = np.arange(rock2_pos[0]-15,rock2_pos[0]+16) 
rock2_yrange = np.arange(rock2_pos[1]-15,rock2_pos[1]+16)
rock3_pos = (120,100)
rock3_xrange = np.arange(rock3_pos[0]-15,rock3_pos[0]+16) 
rock3_yrange = np.arange(rock3_pos[1]-15,rock3_pos[1]+16)
finish_pos = (150,40)
finish_xrange = np.arange(finish_pos[0]-15, finish_pos[0]+16)
finish_yrange = np.arange(finish_pos[1]-15, finish_pos[1]+16)
#count = 0
st_count = 0
car_l=[car_pos]
soft_count = 0
Q_table = [[0 for i in range(4)]for j in range(width * height)]
#Moves.....0 -UP, 1-UP RIGHT, 2 - RIGHT, 3 - DOWN RIGHT, 4- DOWN, 5-DOWN LEFT, 6-LEFT, 7-UP LEFT
'''
Moves 
__
|         (0,-5)  
| (-5, 0)    X    (5, 0)
|         (0, 5)  
__
''' 
'''move_dict = {}
move_dict[(0,-y)] = 0
move_dict[(x,-y)] = 1
move_dict[(x, 0)] = 2
move_dict[(x, y)] = 3
move_dict[(0, y)] = 4
move_dict[(-x,y)] = 5
move_dict[(-x,0)] = 6
move_dict[(-x,-y)] =7
'''
move_dict = {}
move_dict[(0,-3)] = 0

move_dict[(3, 0)] = 1

move_dict[(0, 3)] = 2

move_dict[(-3,0)] = 3

######Dictionary that stores unique ids for each row in the Q table for easy access
positions = []

for i in range(width):
    for j in range(height):
        positions.append(str([i,j]))
INDEX_DICT = dict(zip(positions,range(width * height)))

#print("len_index", len(INDEX_DICT))

#Parameters
gamma = 0.9  
learning_rate = 0.1
epsilon = 0.9
epsilon_decay = 0.9998
epsilon_min = 0.1
count = 0
r_count = 1 #No of rounds
no_of_moves = 0 #No of moves.. cleared after each round
finish_count=0 # No of times the car hits the finish state

#To display the car icon
def car(car_pos):
    screen.blit(carimg, car_pos)
    #count+=1
    
#To display the Rock/barrier Icon    
def rock():
    screen.blit(rockimg, rock1_pos)
    screen.blit(rockimg, rock2_pos)
    screen.blit(rockimg, rock3_pos)
    
#To display the finish State Icon   
def finishl():
    screen.blit(finishimg, finish_pos)

#To display the Game Stats    
def round_count(r_count,no_of_moves,finish_count):
    font = pg.font.Font('freesansbold.ttf', 7) 
    text = font.render('Round: '+str(r_count)+' Moves: '+str(no_of_moves)+' Finish_count: '+str(finish_count), True, (255, 255, 255))
    textRect = text.get_rect()  
    textRect.center = (70,10)
    screen.blit(text, textRect) 

#To generate and random move and update car position during exploration.
def rand_choice(car_l,car_pos):
    temp_pos = car_pos
    while(temp_pos == car_l[-1] or temp_pos[0] < 16 or temp_pos[0] >180 or temp_pos[1] >180 or temp_pos[1] < 16 ):
        action= random.choice([0,1,2,3])
        if action==0:
            x_change,y_change = 0,-3
        elif action==1:
            x_change,y_change = 3,0
        elif action==2:  
            x_change,y_change = 0,3
        elif action==3:  
            x_change,y_change = -3,0
        temp_pos = (car_pos[0]+x_change , car_pos[1]+y_change)
    move = move_dict[(x_change,y_change)]
    #print("rand move", action)
    return temp_pos,move

#To identify the next move from Q table and to update the car position according after taking the move.
def move_from_learning(move, car_pos):
    move_direction = list(move_dict.keys())[list(move_dict.values()).index(move)]
    print("move_direction",move_direction)
    temp_pos = (car_pos[0]+move_direction[0], car_pos[1]+move_direction[1])
    return temp_pos

#To check if the car has touched the finish state
def check_win(car_pos):
    car_l2 = (car_pos[0]-16, car_pos[1]-16)
    car_r2 = (car_pos[0]+16, car_pos[1]+16)
    #Is the vehicle overlapping with Rock1?###################
    if(car_l2[0] in finish_xrange or car_r2[0] in finish_xrange):
        if(car_l2[1] in finish_yrange or car_r2[1] in finish_yrange):
            return True
        else: return False 
    # If one rectangle is above other 
    else:return False
 
#To check if the car has made a collision with the Barrier/Obstacle
def check_collision(car_pos):
    car_l2 = (car_pos[0]-16, car_pos[1]-16)
    car_r2 = (car_pos[0]+16, car_pos[1]+16)
    #Is the vehicle overlapping with Rock1?###################
    if(car_l2[0] in rock1_xrange or car_r2[0] in rock1_xrange):
        if(car_l2[1] in rock1_yrange or car_r2[1] in rock1_yrange):
            return True
        else: return False
    elif(car_l2[0] in rock2_xrange or car_r2[0] in rock2_xrange):
        if(car_l2[1] in rock2_yrange or car_r2[1] in rock2_yrange):
            return True
        else: return False
    elif(car_l2[0] in rock3_xrange or car_r2[0] in rock3_xrange):
        if(car_l2[1] in rock3_yrange or car_r2[1] in rock3_yrange):
            return True
        else: return False
        
#To generate reward based on interaction with the grid elements    
def reward_function(collision,reached_finish):

    reward = 0
    move_penality = -0.2
    reward+=move_penality
    distance_to_finish_old = np.sqrt((car_l[-2][0] - finish_pos[0])**2 + (car_l[-2][1] - finish_pos[1])**2)
    distance_to_finish_new = np.sqrt((car_l[-1][0] - finish_pos[0])**2 + (car_l[-1][1] - finish_pos[1])**2)
    
    distance_to_rock1_old = np.sqrt((car_l[-2][0] - rock1_pos[0])**2 + (car_l[-2][1] - rock1_pos[1])**2)
    distance_to_rock1_new = np.sqrt((car_l[-1][0] - rock1_pos[0])**2 + (car_l[-1][1] - rock1_pos[1])**2)
    
    distance_to_rock2_old = np.sqrt((car_l[-2][0] - rock2_pos[0])**2 + (car_l[-2][1] - rock2_pos[1])**2)
    distance_to_rock2_new = np.sqrt((car_l[-1][0] - rock2_pos[0])**2 + (car_l[-1][1] - rock2_pos[1])**2)
    
    #To check if the car is moving closer or away from the finish state
    if distance_to_finish_old>distance_to_finish_new:
        reward+=1
        #distance_old = distance_new
    elif distance_to_finish_old<=distance_to_finish_new:
        reward-=1
     
    #To check if the car is moving closer or away from the obstacles/barriers
    '''if distance_to_rock1_old<distance_to_rock1_new:
        reward+=0.3
        #distance_old = distance_new
    elif distance_to_rock1_old>=distance_to_rock1_new:
        reward-=0.3
        
    if distance_to_rock2_old<distance_to_rock2_new:
        reward+=0.3
        #distance_old = distance_new
    elif distance_to_rock2_old>=distance_to_rock2_new:
        reward-=0.3'''
        
     #To check if the car has successfully touched the finish state
    if reached_finish:
        reward+=10
    #To check if the car made a collision
    if collision:
        reward-=20

    return reward
        
    
def qtable(car_l, reward, move):
    
    current_state = [car_l[-1][0], car_l[-1][1]]
    
    row_index_new = INDEX_DICT[str(current_state)]
    
    prev_state = [car_l[-2][0], car_l[-2][1]]

    row_index_old = INDEX_DICT[str(prev_state)]
    
    #Bellman's equation for Q Update
    q_value = (1 - learning_rate) * Q_table[row_index_old][move] + learning_rate * (reward + gamma * max(Q_table[row_index_new]))
    #print(q_value)
    
    #Update Qtable with the calculated Q value
    Q_table[row_index_old][move]= q_value
    #print("Q_Value",q_value)
    #print("Shape", len(Q_table[0]))

# To check if we are in exploration stage or exploitation and to perform epsilon decay.    
def epsilon_update(epsilon):
    if epsilon > epsilon_min:
        print("_______________|Exploration|_________________")
        epsilon *= epsilon_decay
        print("epsilon in func:", epsilon)
        return epsilon
    else:
        print("_______________|Exploitation|_________________")
        epsilon *= epsilon_decay
        print("epsilon:", epsilon)
        return epsilon
        
move_list = []

#main control loop
while running:
    no_of_moves+=1
    
    #Exploration Stage
    if epsilon>epsilon_min:
        car_pos, move = rand_choice(car_l, car_pos)
        #print("move", move)
        #(carx,cary) = car_l[-1]
        car_l.append(car_pos)
        #qtable(car_l, finish_pos, st_count)
        st_count += 1
        
        screen.fill((0,0,0))
        
        collision = check_collision(car_pos)
        reached_finish = check_win(car_pos)
        
        if reached_finish:
            finish_count+=1
            
        reward = reward_function(collision,reached_finish)
        qtable(car_l, reward, move)
        
        if collision or reached_finish or no_of_moves == 2000:
            car_pos = car_l[0] 
            car_l = [car_pos]  
            r_count +=1
            no_of_moves=0
            epsilon = epsilon_update(epsilon)
            screen.fill((255,0,0))
    
        round_count(r_count,no_of_moves,finish_count) 
        
        #Saving training progress
        if r_count==1000:
            open_file = open("Qtable_1000.pkl","wb")
            pickle.dump(Q_table,open_file)
            open_file.close() 
        if r_count==3000:
            open_file = open("Qtable_3000.pkl","wb")
            pickle.dump(Q_table,open_file)
            open_file.close()
        if r_count==4500:
            open_file = open("Qtable_4500.pkl","wb")
            pickle.dump(Q_table,open_file)
            open_file.close()
        if r_count==10000:
            open_file = open("Qtable_10000.pkl","wb")
            pickle.dump(Q_table,open_file)
            open_file.close()
        #print(reward)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                
        #to display car
        car(car_pos)   
        #to display rocks     
        rock()
        #to display finish flag
        finishl()
        pg.display.update()
        
    #Exploitation Stage    
    elif epsilon<=epsilon_min:
        if count == 0:
            open_file = open("Qtable_3rocks.pkl","wb")
            pickle.dump(Q_table,open_file)
            open_file.close()
            current_pos = INDEX_DICT[str([car_l[0][0],car_l[0][1]])]
            open_file_read = open("Qtable_3rocks.pkl","rb")
            saved_Qtable = pickle.load(open_file_read)
            open_file_read.close()
        else:  
            current_pos = INDEX_DICT[str([car_l[-1][0],car_l[-1][1]])]
        
        move = saved_Qtable[current_pos].index(max(saved_Qtable[current_pos]))
        print(move)
        move_list.append(move)
        
        #To check if the car learnt to move in loops
        '''soft_count+=1
        if soft_count>=4:#len(move_list)>4:
            soft_count=0
            if (move_list[-4]==move_list[-2]) and (move_list[-3]==move_list[-1]):
                print("sl")
                car_pos, move = rand_choice(car_l, car_l[-1])
                move_list[-1] = move
            elif len(move_list)>6:
                print("sl")
                if (move_list[-6]==move_list[-3]) and (move_list[-5]==move_list[-2]) and (move_list[-4]==move_list[-1]):
                    car_pos, move = rand_choice(car_l, car_l[-1])
                    move_list[-1] = move'''
        
        #print(Q_table[current_pos])
        #print("move",move)
        new_pos = move_from_learning(move, car_l[-1])
        
        if new_pos[0] < 16 or new_pos[0] >180 or new_pos[1] >180 or new_pos[1] < 16:
            #print('bsl')
            new_pos, move = rand_choice(car_l, car_l[-1]) 
        car_l.append(new_pos)
        screen.fill((0,0,0))
        collision = check_collision(car_pos)
        reached_finish = check_win(car_pos)
        if reached_finish:
            finish_count+=1
        round_count(r_count,no_of_moves,finish_count)   

        if collision or reached_finish or no_of_moves == 4000:
            car_pos = car_l[0] 
            car_l = [car_pos]  
            r_count +=1
            no_of_moves=0
            epsilon = epsilon_update(epsilon)
            screen.fill((255,0,0))
        if r_count>40000:
                running = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                print(finish_count)
                running = False
         
        #to display car
        count=1
        car(new_pos)   
        #to display rocks     
        rock()
        #to display finish flag
        finishl()
        pg.display.update()
       
        
        
    