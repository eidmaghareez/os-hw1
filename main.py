import operator
import sys
import copy


#function to call to end the program
def progdone():
    print("Program is done ...\nexiting now")
    #this function ends the program
    exit()


#priority scheduling algorithm
def runpr(processes):
    #global to cpu time so we can edit it from inside this function
    global cputime
    #create variable named currentp and set it as the first process of the ready queue
    currentp = processes[0]
    #variable ptime and set it to the full time the process will take on the cpu
    ptime = currentp.totalcpu
    #variable itime and set it to the full time the process will take on the i/o
    itime = currentp.totalio
    #if the process was never run before then set its first run time to the time of the cpu
    if (currentp.updatefirstrun == True):
        currentp.firstrun = cputime
    #increase the cpu time by the total time the process will take on the cpu
    cputime += ptime
    #set the first run time of the next process to the cpu time
    firstrunnext = cputime
    #increase the cpu time by the time the current process will spend on the i/o because while that is happening the next process in the queue will be using the cpu
    cputime += itime
    #global to the avg turnaround time and avg response time because we want to update them
    global avgturnaround
    global avgresponsetime
    #set the process finish time to the time of the cpu at that point
    currentp.donetime = cputime
    #add the response time of the process/(number of processes) to the avg response time
    avgresponsetime += currentp.responsetime() / nprocesses
    #add the turnaround time of the process/(number of processes)to the avg turnaround time
    avgturnaround += currentp.turnaroundtime() / nprocesses
    #add the current process to the cputimeline function which will print what happened in the cpu
    cputimeline.append(currentp)
    #if the queue has more than one element
    if len(processes) > 1:
        #variable nextp to the next process in the queue
        nextp = processes[1]
        #if the next process total time on the cpu is more of equal to the time the current process will spend on the i/o then subtract the next process total cputime by that time the current process will spend on i/o
        if (nextp.totalcpu >= itime):
            nextp.totalcpu -= itime
        #if its less than the itime then update the itime by subtracting the next process total cpu time from it and set the next process totalcpu to 0
        else:
            itime = itime - nextp.totalcpu
            nextp.totalcpu = 0
            #if the queue is equal to 3 or more then also subtract the next next process total cpu time by itime
            if (len(processes) >= 3):
                processes[2].totalcpu -= itime
        #update the next process first run to the firstrunnext variable we declared above
        nextp.firstrun = firstrunnext
        #update the updatefirstrun to false so it does not enter this loop again
        nextp.updatefirstrun = False
        #append the current process and next process to cputimeline so we can print it later
        cputimeline.append(currentp)
        cputimeline.append(nextp)
        cputimelineitime.append(itime)
    #remove the current process from the queue
    processes.pop(0)


#function that takes some information about a process and returns a process object with that info
def createprocess(priority, numberofbursts, bursts, arrivetime):
    process = pcb(priority, numberofbursts, bursts, arrivetime)
    return process


# two functions to print whats happening in the cpu
def printcputimeline2(currentp, nextp, itime):
    print("While process No.", currentp.pid,
          " was waiting for i/o Process No.", nextp.pid, " ran for", itime,
          "ms on the Cpu and now its remaining cpu time is", nextp.totalcpu,
          "ms")


def printcputimeline(process):
    print("\n\nProcess No.", process.pid, "\narrived at ", process.arrivetime,
          "ms\nRan for first time at ",
          process.firstrun, "ms\nTotal time process should run on cpu",
          sum(process.cpu), "ms\nTotal time process should wait for i/o ",
          sum(process.io), "ms\nRan for ", process.totalcpu,
          "ms on the cpu \nWaited for ", process.totalio,
          "ms on i/o  \nProcess finished at ", process.donetime,
          "ms \nResponse time : ", process.responsetime(),
          "ms\nTurnaround time : ", process.turnaroundtime())


#processes class
class pcb:
    def responsetime(self):
        rt = self.firstrun - self.arrivetime
        return rt

    def getid(self):
        global id
        id += 1
        return id

    def changeturn(self):
        if self.turn == "cpu":
            self.turn = "io"
        elif self.turn == "io":
            self.turn = "cpu"

    def changecurrcpuio(self):
        if (self.cpu[self.currcpuburst] <= 0):
            self.changeturn()
            if (self.currcpuburst + 1 <= self.ncpuburst):
                self.currcpuburst += 1
        elif self.io[self.currioburst] <= 0:
            self.changeturn()
            if (self.currioburst + 1 <= self.nioburst):
                self.currioburst += 1

    def turnaroundtime(self):

        #turnaround time
        ta = self.donetime - self.arrivetime
        return ta

    def __init__(self,
                 priority,
                 numberofbursts,
                 bursts,
                 arrivetime,
                 donetime=0):
        self.pid = self.getid()
        self.firstrun = arrivetime

        self.donetime = donetime
        self.numberofbursts = numberofbursts
        self.priority = priority
        self.ncpuburst = 0
        self.nioburst = 0
        self.cpu = []
        self.updatefirstrun = True
        self.io = []
        self.turn = "cpu"
        self.arrivetime = arrivetime
        self.burst = [None] * int(numberofbursts)
        for i in range(int(numberofbursts)):
            if (i % 2 == 0):
                self.ncpuburst += 1
            else:
                self.nioburst += 1
        for i in range(len(bursts)):
            self.burst.append(bursts[i])
            if (i % 2 == 0):
                self.cpu.append(bursts[i])
            else:
                self.io.append(bursts[i])
        self.totalcpu = sum(self.cpu)
        self.totalio = sum(self.io)
        self.currcpuburst = 0
        self.currioburst = 0

    def info(self):
        print("Pid : ", self.pid, "\nPriority : ", self.priority,
              "\nNumber of bursts : %d " % int(self.numberofbursts),
              "\nNo.Cpu bursts : ", self.ncpuburst, "\nNo.I/O bursts : ",
              self.nioburst, "\nCpu Bursts : ", self.cpu, "\nI/O Bursts : ",
              self.io, "\nArrive time : ", self.arrivetime, "\n\n")




algorithm = str((sys.argv[1]))
quantum = int(sys.argv[2])
infile = str((sys.argv[3]))
inputfile = open(infile, "r")
input = inputfile.readlines()



if algorithm == ("PR"):
    processes = []
    nprocesses = 0
    readyqueue = []
    arrivetime = 0
    cputime = 0
    id = 0
    avgturnaround = 0
    avgresponsetime = 0
    idletime = 0
    totalbursttime = 0
    cputimeline = []
    cputimelineitime = []
    for i in range(len(input)):
        line = input[i]
        # print(line, end="")
        func = line[:4]
        if func == "proc":
            nprocesses += 1
            priority = line[5]
            number_of_bursts = line[7]
            line = line.strip("\n")
            bursts = line[9:].split(" ")
            bursts = list(map(int, bursts))
            totalbursttime += sum(bursts)
            process = createprocess(priority, number_of_bursts, bursts,
                                    arrivetime)
            processes.append((process))
            # processes[nprocesses - 1].info()
            readyqueue.append(processes[nprocesses - 1])
        elif func == "idle":
            idle = int(line[5:].strip(" \n"))
            # print("idle for : ", idletime, "ms")
            idletime += idle
            arrivetime += idle
        else:
            isprogdone = True

        readyqueue = sorted(readyqueue,
                            key=operator.attrgetter("priority", "pid"))

    for i in range(len(readyqueue)):
        runpr(readyqueue)
    cpuutilization = totalbursttime / (totalbursttime + idletime)
    print("\n\nInput file name : ", infile, "\nCpu scheduling algorithm : ",
          algorithm, "\nCpu utilization : ", cpuutilization,
          "\nAvg. Turnaround time : ", avgturnaround,
          "\nAvg. Response time in R queue : ", avgresponsetime,
          "\nCPU timeline : \n")
    i = 0
    j = 0
    while i < len(cputimeline):
        printcputimeline(cputimeline[i])
        i += 1
        if (i < len(cputimeline) - 2):
            printcputimeline2(cputimeline[i], cputimeline[i + 1],
                              cputimelineitime[j])
            i += 2
            j += 1
    if ((len(readyqueue) == 0) and isprogdone == True):
        progdone()



if algorithm ==("RR"):
    processes = []
    nprocesses = 0
    readyqueue = []
    arrivetime = 0
    cputime = 0
    id = 0
    avgturnaround = 0
    avgresponsetime = 0
    idletime = 0
    totalbursttime = 0
    cputimeline = []
    cputimelineitime = []
    #loop through the input to get processes/idletime/if the program is done
    for i in range(len(input)):
        #line the current line in the input we are looping through
        line = input[i]
        #function is what the line is telling us to do either create a process or idle or exit and we do it by taking the first 4 characters of the line
        func = line[:4]
        #if function is equal to proc then we should create a new process and in this if statement we gather info required to create a process
        if func == "proc":
            #increase number of processes by 1
            nprocesses += 1
            #get total number of bursts for each process
            number_of_bursts = line[7]
            #remove the newline from the line we are working on
            line = line.strip("\n")
            #create a list named bursts and we add the bursts to it by seperating each burst when we see a space
            bursts = line[9:].split(" ")
            #turn the burst list into integers
            bursts = list(map(int, bursts))
            #add the total time that this process will run for (cpu time and i/o time)
            totalbursttime += sum(bursts)
            #create a new process and add the number of bursts / burst list / when the process arrived and add priority to 0 because we don't care about that in Round Robin
            process = createprocess(0, number_of_bursts, bursts, arrivetime)
            #add the process we created to the processes list
            processes.append((process))
            #add the process to the ready queue
            readyqueue.append(processes[nprocesses - 1])
        #else if the func is idle
        elif func == "idle":
            #take the idle time from the line by stripping it from \n and turning it to an integer
            idle = int(line[5:].strip(" \n"))
            #adding the idle time to the total idle time for cpu
            idletime += idle
            #adding the idle time to the arrive time which was set to 0 so when a new process arrives its arrive time is set to the new arrivetime value
            arrivetime += idle
        else:
            isprogdone = True
    readyqueue2=[]
    # readyqueue2.extend(readyqueue)
    readyqueue2=copy.deepcopy(readyqueue)
    
    
    #while the readyqueue is not empty
    version = 1
    if version == 1:
        while (readyqueue):
            cp = readyqueue[0]
            if (cp.updatefirstrun == True):
                
                cp.firstrun = cputime
                cp.updatefirstrun = False
                avgresponsetime += cp.responsetime() / nprocesses
        
            temp = cp.totalcpu
            if (quantum > cp.totalcpu):
               
                cp.totalcpu = 0
            else:
                
                cp.totalcpu -= quantum
    
            cputime += quantum
            if (cp.totalcpu > 0):
                readyqueue.append(cp)
                
            else:
                cp.donetime = cputime
                avgturnaround += (cp.turnaroundtime() / nprocesses)
            if (len(readyqueue) > 1 and temp < quantum):
                np = readyqueue[1]
                if (np.firstrun == True):
                    np.firstrun = cputime - (quantum - temp)
                    np.updatefirstrun == False
                    avgresponsetime += np.responsetime() / nprocesses
    
                np.totalcpu -= (quantum - temp)
            readyqueue.pop(0)
    
    
    
        cpuutilization = totalbursttime / (totalbursttime + idletime)
        print("\n\nInput file name : ", infile, "\nCpu scheduling algorithm : ",
              algorithm, "\nCpu utilization : ", cpuutilization,
              "\nAvg. Turnaround time : ", avgturnaround,
              "\nAvg. Response time in R queue : ", avgresponsetime,
              "\nCPU timeline : \n")
        print("1-All Processes general information")
        for i in range(len(readyqueue2)):
         readyqueue2[i].info()
    
        cputime = 0
        print("2-Cpu timeline")
        while (readyqueue2):
            #cp -> current process we are running
            cp = readyqueue2[0]
            print("\n\ncurrent process running is process No.", cp.pid)
            #if the process never ran before then set its first run time to the curr cputime
            if (cp.updatefirstrun == True):
                print("running for the first time on the cpu at time : ", cputime,
                      "ms")
                cp.firstrun = cputime
                cp.updatefirstrun = False
                avgresponsetime += cp.responsetime() / nprocesses
            #decrease the total time the process should run on the cpu by the timeslice(quantum)
            print("total cpu time is : ", cp.totalcpu, "ms")
            temp = cp.totalcpu
            if (quantum > cp.totalcpu):
                print("it ran for ", quantum - temp, "ms this time slice")
                cp.totalcpu = 0
            else:
                print("it ran for ", quantum, "ms this time slice")
                cp.totalcpu -= quantum
    
            cputime += quantum
            if (cp.totalcpu > 0):
                readyqueue2.append(cp)
                print("remaining time for this process is ", cp.totalcpu, "ms")
            else:
                print("process No.", cp.pid, "IS DONE at time : ", cputime, "ms")
                cp.donetime = cputime
                avgturnaround += (cp.turnaroundtime() / nprocesses)
            if (len(readyqueue2) > 1 and temp < quantum):
                np = readyqueue2[1]
                print("In the same")
                if (np.firstrun == True):
                    np.firstrun = cputime - (quantum - temp)
                    np.updatefirstrun == False
                    avgresponsetime += np.responsetime() / nprocesses
    
                np.totalcpu -= (quantum - temp)
            readyqueue2.pop(0)
    if ((len(readyqueue) == 0) and isprogdone == True):
        progdone()
