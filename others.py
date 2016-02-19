import socket, string, sys
import os, collections
import re, signal
import select, tempfile, time
from datetime import datetime
from optparse import OptionParser
from communication import send,receive


def parse(data, sender, channelMap):
    command = data.split()[0]        
    count = len(re.findall(r'\w+',data))
    if command == 'CREATE':
        if count > 2 or count == 1:
            msg = "Invalid Command\n Usage: CREATE roomname"
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(sender, new_message)
        else:    
            sender_name = return_user_name(sender, channelMap)
            create_channel(data.split()[1], sender_name, sender, channelMap)
            
    elif command == 'LEAVE':
        if count > 2 or count == 1:
            msg = "Invalid Command\n Usage: LEAVE roomname"
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(sender, new_message)
        else:
            sender_name = return_user_name(sender, channelMap)
            leave_channel(data.split()[1], sender_name, sender, channelMap)

    elif command == 'DISCONNECT':
        if count > 1:
            msg = "Invalid Command\n Usage: DISCONNECT"
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(sender, new_message)
            
    elif command == 'JOIN':
        if count == 2:
            sender_name = return_user_name(sender, channelMap)
            join_channel(data.split()[1], sender_name, sender, channelMap)
        elif count == 3:
            sender_name = return_user_name(sender, channelMap)
            join_channel(data.split()[1], sender_name, sender, channelMap)
            join_channel(data.split()[2], sender_name, sender, channelMap)
        elif count == 4:
            sender_name = return_user_name(sender, channelMap)
            join_channel(data.split()[1], sender_name, sender, channelMap)
            join_channel(data.split()[2], sender_name, sender, channelMap)
            join_channel(data.split()[3], sender_name, sender, channelMap)
        elif count == 5:
            sender_name = return_user_name(sender, channelMap)
            join_channel(data.split()[1], sender_name, sender, channelMap)
            join_channel(data.split()[2], sender_name, sender, channelMap)
            join_channel(data.split()[3], sender_name, sender, channelMap)
            join_channel(data.split()[4], sender_name, sender, channelMap)
        else:
            msg = "Invalid Command to JOIN rooms. you must provide atleast one roomname\n Usage: JOIN roomname roomname roomname "
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(sender, new_message)

    elif command == 'LIST':
        if count > 1:
            msg = "Invalid Command to LIST rooms. \n Usage: LIST"
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(sender, new_message)
        elif count == 1:
            list_rooms(sender, channelMap)

    elif command == 'MEMBERS':
        if count > 2 or count < 2:
            msg = "Invalid Command to list room members\n Usage: MEMBERS roomname"
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(sender, new_message)
        elif count == 2:
            list_members(sender, data.split()[1], channelMap)
            

    elif command == 'PRIVATE-MSG':
        if count >= 4:
            mess = re.sub(data.split()[0],'',data)
            message = re.sub(mess.split()[0],'',mess)
            private_message(message, sender, data.split()[1], channelMap)
        else:
            msg = "Invalid Command to send private message\n Usage: PRIVATE-MSG username message"
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(sender, new_message)
        

    elif command == 'CHANNEL-MSG':
        if count >= 4:
            mess = re.sub(data.split()[0],'',data)
            message = re.sub(mess.split()[0],'',mess)
            channel_message(message, sender, data.split()[1], channelMap)
        elif count >= 6:
            channel_message(data.split()[2], sender, data.split()[1], channelMap)
            channel_message(data.split()[4], sender, data.split()[3], channelMap)                            
        else:
            msg = "Invalid Command to send channel message\n Usage: CHANNEL-MSG channelname message or CHANNEL-MSG channelname message channelname message"
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(sender, new_message)
                
    elif command == 'HELP':
        if count == 1:
            help_message(sender)
        else:
            msg = "Invalid Command for help\n Usage: HELP "
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(sender, new_message)
            
    elif command == 'BCAST-MSG':
        if count == 1:
            msg = "Invalid Command for Broadcast\n Usage: BCAST message "
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(sender, new_message)
        else:
            mess = re.sub(data.split()[0],'',data)
            broadcast_message(mess, sender, channelMap)
            
    else:
        help_message(sender)

   
        
def invalid_command(socket):
    msg = "PLEASE USE THE HELP BUTTON TO SEE A LIST OF AVAILABLE COMMANDS"
    new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
    send(socket, new_message)
        
def help_message(socket):
    msg = """
            WELCOME TO THE IRC HELP\n
            CREATE A ROOM OR JOIN A ROOM TO START A CONVERSATION
            TO LIST ALL ROOMS. USE: 'LIST' \n
            TO LIST ALL MEMEBERS OF A ROOM. USE: 'MEMBERS roomname' \n
            TO CREATE A ROOM. USE: 'CREATE roomname' NOTE: IF ROOM ALREADY EXISTS YOU'LL JOIN IT. \n
            TO JOIN A ROOM. USE: 'JOIN roomname' \n
            TO JOIN MULTIPLE ROOMS. USE: 'JOIN roomname roomname roomname' \n
            TO LEAVE A ROOM. USE: 'LEAVE roomname' \n
            TO DISCONNECT FROM THE IRC. USE: 'DISCONNECT' \n
            TO SEND A PRIVATE MESSAGE TO ANOTHER CLIENT. USE: 'PRIVATE-MSG username message' \n
            TO SEND A MESSAGE TO A CHANNEL. USE: 'CHANNEL-MSG channelname message.' \n
            TO SEND DISTINCT MESSAGE TO MULTIPLE CHANNELS. USE: 'CHANNEL-MSG channelname message channelname message.' \n
        """
    new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
    send(socket, new_message)
    
def check_channel_exist(query, channelMap):    # Return true if a room already exists
    if query in channelMap.keys():
        return True
    else:
        return False

def disconnect(socket, channelMap):
    name = return_user_name(socket, channelMap)
    for key,values in channelMap.items():
        channelMap[key].remove([name,socket])
    socket.close()
    message = '%s just left the IRC'
    affected_sockets = return_channel_sockets('Global', channelMap)
    connbroadcast = '\n[' + 'SERVER@6510' + ']>> ' + message
    for o in affected_sockets:
        if o != socket:
            send(o, connbroadcast)
    
def check_user_inchannel(clientname, socket, channelname, channelMap):
    if check_channel_exist(channelname, channelMap) == True:
        if [clientname,socket] in channelMap[channelname]:
            return True
        else:
            return False
    else:
        #send to requesting socket, if i implement this, but this is mainly for other functions
        msg = "Checking for user in room that doesn't exist"
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
        send(socket, new_message)
    
def join_channel(channelname, client, socket, channelMap):    #two steps, check if the room exists and add the client if it des
    if check_channel_exist(channelname, channelMap) == True:
        if check_user_inchannel(client, socket, channelname, channelMap) == True:
            #Send to requesting socket
            msg = "User already in channel"
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(socket,new_message)
            return channelMap
        else:
            channelMap[channelname].append([client,socket])
            # send first message to requesting socket and second to other sockets in group
            msg = "Joined Room !"
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(socket, new_message)
            msg2= "%s just joined Room - %s" % (client, channelname)
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg2
            affected_sockets = return_channel_sockets(channelname, channelMap)
            for o in affected_sockets:
                if o != socket:
                    send(o, new_message)
            return channelMap
    else:
        # Send message to Requesting socket
        msg = "Room Does Not Exist !"
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
        send(socket,new_message)
        return channelMap

def create_channel(channelname, client, socket, channelMap):
    if check_channel_exist(channelname, channelMap) == False:
        channelMap[channelname] = [[client,socket]]
        msg = "Room %s Created" % (channelname)
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
        send(socket,new_message)
        return channelMap
    else:
        msg = "Room is Existing....Joining Room"
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
        send(socket, new_message)
        join_channel(channelname, client, socket, channelMap)

def leave_channel(channelname, client, socket, channelMap):
    if check_user_inchannel(client, socket, channelname, channelMap) == True:
        channelMap[channelname].remove([client,socket]) #remove requested client
        if not channelMap[channelname]: # Delete room if last person leaves
            channelMap.pop(channelname)
            msg = 'You are the last person in the room and you left. Room Dissolved'
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(socket, new_message)
            return channelMap  #No need for message, no-one to show it to
        else:
            send(socket, '\n[' + 'SERVER@6510' + ']>> You left the room')
            msg = "%s Left the room - %s" % (client,channelname)
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            affected_sockets = return_channel_sockets(channelname, channelMap)
            for o in affected_sockets:
                send(o, new_message)
                # send message to all sockets still in channel instead
            return channelMap
    else:
        msg = "You cannot leave the room you're not in !"
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
        send(socket, new_message)
        return channelMap
            
def list_rooms(socket, channelMap):
    sample = []
    for key,values in channelMap.items():
        if key != 'Global':
            sample.append(key)
    if sample:
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + 'Currently available rooms are: \n' + '\n'.join(sample)
        send(socket,new_message)
    elif not sample:
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + 'There are no rooms'
        send(socket,new_message)
    
def list_members(socket, channelname, channelMap):
    if check_channel_exist(channelname, channelMap) == True:
        sample_msg = []
        for [value1,value2] in channelMap[channelname]:
            sample_msg.append(value1)
        if sample_msg:
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + 'Members in ' + channelname + ' are: \n' + '\n'.join(sample_msg)
            send(socket,new_message)
        elif not sample_msg:
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + 'NO Members in' + ' ' + channelname
            send(socket,new_message)
    else:
        msg = "Room Does not exist !"
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
        send(socket, new_message)   
        
def return_user_socket(client, channelMap):
    for [value1,value2] in channelMap['Global']:
        if value1 == client:
            return value2

def return_user_name(client_socket, channelMap):
    for [value1,value2] in channelMap['Global']:
        if value2 == client_socket:
            return value1
    
def channel_message(message, sending_client, channelname, channelMap):
    client = return_user_name(sending_client, channelMap)
    affected_sockets = return_channel_sockets(channelname, channelMap)
    if affected_sockets:
        if check_user_inchannel(client, sending_client, channelname, channelMap) == False:
            msg = "You cannot send a message to a channel you're not in!"
            new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
            send(sending_client,new_message)
        else:
            new_message = '\n[' + client + ']>> ' + message
            for o in affected_sockets: #send channel message to all members except sending user
                if o != sending_client:
                    send(o, new_message)
    else:
        msg = "Either you have spelt the channel wrongly or it doesn't exist"
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
        send(sending_client,new_message)


def private_message(message, send_from, send_to, channelMap):
    sender = return_user_name(send_from, channelMap)
    receiver = return_user_socket(send_to, channelMap)
    if receiver:
        new_message = '\nPRIVATE[' + sender + ']>> ' + message
        send(receiver, new_message)
    else:
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + 'User Does not Exist'
        send(send_from,new_message)
        
    

def return_channel_sockets(channelname, channelMap):
    sockets = []
    if check_channel_exist(channelname, channelMap) == True:
        for [value1,value2] in channelMap[channelname]:
            sockets.append(value2)
        return sockets # to be used for message relay and etc...
    else:
        return sockets
    
def broadcast_message(message, sender, channelMap):
    sender_name = return_user_name(sender, channelMap)
    affected_sockets = return_channel_sockets('Global', channelMap)
    connbroadcast = '\n[' + sender_name + ']>> ' + message
    for o in affected_sockets:
        if o != sender:
            send(o, connbroadcast)
