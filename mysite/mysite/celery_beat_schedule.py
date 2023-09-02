#This is where all celery settings.py is. For faster deployment


#CELERY_BEAT_SCHEDULE = {  # scheduler configuration
#    "Task_two_schedule": {  # whatever the name you want
#        "task": "SuperDuperVPN.tasks.HelloWorld",  # name of task with path
#        "schedule": 10,  # 30 runs this task every 30 seconds
#        "args": {},  # arguments for the task
#    },
#}

CELERY_BEAT_SCHEDULE = {  # scheduler configuration
    
    #for loading data from wg log file created by the shell scripts
    "Load_Host_Wireguard_Logs_every_minute":{
        "task":"SuperDuperVPN.tasks.Load_Host_Wireguard_Logs",
        "schedule":60,
        "args":{3600},
    },

    #Load_Host_Wireguard_Logs (database) to actual usable data
    "Calculate_PeerUsageData":{
        "task":"SuperDuperVPN.tasks.Calculate_PeerUsageData",
        "schedule":60,
        "args":{},
    },
}