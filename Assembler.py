R_Instuctions=['add','sub','slt','and','or','sll','jr']
R_Funct={'add':'100000','sub':'100010','and':'100100','slt':'101010','or':'100101','sll':'000000','jr':'001000'}
I_Instuctions=['lw','sw','addi','ori']
I_Op={'lw':'100011','sw':'101011','beq':'000100','bne':'000101','addi':'001000','ori':'001101'}
J_Op={'j':'000010','jal':'000011'}
Registers = {'$0':'00000' ,'$zero':'00000','$at':'00001','$v0':'00010','$v1':'00011','$a0':'00100','$a1':'00101','$a2':'00110','$a3':'00111',
             '$t0':'01000','$t1':'01001','$t2':'01010','$t3':'01011','$t4':'01100','$t5':'01101','$t6':'01110','$t7':'01111',
             '$s0':'10000','$s1':'10001','$s2':'10010','$s3':'10011','$s4':'10100','$s5':'10101','$s6':'10110','$s7':'10111',
             '$t8':'11000','$t9':'11001','$k0':'11010','$k1':'11011','$gp':'11100','$sp':'11101','$fp':'11110','$ra':'11111'}

def is_Rtype(instruction):
   for i in R_Instuctions:
     if (i==instruction.split()[0]):
        return 1

def decimalToBinary(n): 
    binary=bin(n).replace("0b", "")
    if (len(binary)==1):
       binary = '0000'+ binary
    if (len(binary)==2):
        binary = '000'+ binary
    if (len(binary)==3):
        binary = '00'+ binary
    if (len(binary)==4):
        binary = '0'+ binary
    return binary #type:string
    
def R_Type_Conversion(instruction):
    instParts=instruction.replace(',',' ').split()
    if (instParts[0]=='sll'): #sll
            op='000000'
            rs='00000'
            rt=Registers[instParts[2]]
            rd=Registers[instParts[1]]
            shamt=decimalToBinary(int(instParts[3]))
            funct=R_Funct[instParts[0]]
            return  op + rs + rt + rd + shamt + funct
    elif (instParts[0]=='jr'): #jr
            op='000000'
            rs=Registers[instParts[1]]
            rt='00000'
            rd='00000'
            shamt='00000'
            funct=R_Funct[instParts[0]]
            return  op + rs + rt + rd + shamt + funct
    else: ## add sub slt and or
         op='000000'
         rs=Registers[instParts[2]]
         rt=Registers[instParts[3]]
         rd=Registers[instParts[1]]
         shamt='00000'
         funct=R_Funct[instParts[0]]
         return  op + rs + rt + rd + shamt + funct


def decimalToBinarySignExtend(n,nbits):
        if (n[0]=='-'): #negative numbers
              binary=bin(int(n) & 0b1111111111111111) #bitwise and to get positive decimal whose binary equals the negative num
              binary=binary.replace('0b','')
        else: #positive numbers
              binary=bin(int(n))
              binary=binary.replace('0b','')
              for i in range(nbits-len(binary)): ##zero extend for positive numbers
                  binary = '0' + binary
        return binary

def is_Itype(instruction):
   for i in I_Instuctions:
    if (i==instruction.split()[0]):        
        return 1
    
def I_Type_Conversion(instuction):
    instParts=instuction.replace(',',' ').replace('(',' ').replace(')',' ').split()  
    op=I_Op[instParts[0]]
    if(instParts[0]=='addi' or instParts[0]=='ori'): #addi ori
        rs=Registers[instParts[2]]
        rt=Registers[instParts[1]]
        immediate=decimalToBinarySignExtend(instParts[3],16)
        return op + rs + rt +immediate
    if(instParts[0]=='lw' or instParts[0]=='sw'):
        rs=Registers[instParts[3]]
        rt=Registers[instParts[1]]
        immediate=decimalToBinarySignExtend(instParts[2],16)
        return op + rs + rt +immediate

def findlabels(liness): #takes all lines and return dic of labels:linenum
    LabelsDic={}
    linenumber=0
    lines2=liness[:]
    for i in range(len(lines2)):
        if (":" in lines2[i]):
            lines2[i]=lines2[i][0:lines2[i].find(":")].lower()
            LabelsDic[lines2[i]]=linenumber #integer of line number
        linenumber = linenumber + 1
    return LabelsDic


def branches_conversion(pc,instruction,lines):
     instparts=instruction.replace(',',' ').split()
     op=I_Op[instparts[0]]
     if (instparts[0]=='beq'):
            rs=Registers[instparts[1]]
            rt=Registers[instparts[2]]
            labelsbeq = findlabels(lines)
            i=labelsbeq[instparts[3]]
            offset=decimalToBinarySignExtend(str(i-pc-1),16)
            return op+rs+rt+str(offset)
     elif(instparts[0]=='bne'):
            rs=Registers[instparts[1]]
            rt=Registers[instparts[2]]
            labelsbeq = findlabels(lines)
            i=labelsbeq[instparts[3]] 
            offset=decimalToBinarySignExtend(str(i-pc-1),16)
            return op+rs+rt+str(offset)

def jumps_conversion(instruction,lines):
     instparts=instruction.replace(',',' ').split()
     op=J_Op[instparts[0]]
     label_address = findlabels(lines)  ## dict of lines and their adresses
     i=label_address[instparts[1]] #line number
     address= decimalToBinarySignExtend(str(i*4),32) ##multiply by 4 and extend to get memory adress
     address = address[4:] ##remove 4 bits left
     address = address[:-2] ## remove 2 bits right\
     return op+address

   
def main():
    assemblyfile = 'assembly.txt'
    binaryfile= 'binary.txt'
    pcfile='PC.txt'
    toinstmemfile='_ToInstMem.txt'
    binary=[]
    lines=[]
    lines2=[]
 
    with open(assemblyfile,'r') as A:
        lines=A.readlines() 
        lines2=lines[:] ## copies lines to lines2 to remove labels from lines


        for i in range(len(lines2)):
            if (":" in lines2[i]): #if inst starts with label > inst without label
                  lines2[i]=lines2[i].rsplit(':')[1] #inst without label
            
            lines2[i]=lines2[i].replace('\n',' ') .lower()
            instParts=lines2[i].replace(',',' ').split()
            print lines[i]
            if (len(lines[i].split())==1):
             lines2[i]='sll $zero, $zero, 0' # for nop
            if (is_Rtype(lines2[i])): ##Convert R Instructions
               binary.append(R_Type_Conversion(lines2[i]))
            elif (is_Itype(lines2[i])):  ##Convert I Instructions
               binary.append(I_Type_Conversion(lines2[i]))
            elif(instParts[0]=='beq' or instParts[0]=='bne'): ##Convert Branches
              binary.append(branches_conversion(i,lines2[i],lines))
            elif(instParts[0]=='j' or instParts[0]=='jal'): ##Convert Jumps
              binary.append(jumps_conversion(lines2[i],lines))
              

    
    with open(binaryfile,'w') as B: ###### Machine Code File
       for i in range(len(binary)):
          B.write(str(binary[i])+'\n')
          print binary[i]
          
    with open(toinstmemfile,'w') as D: ###### input to processor
        for i in range(len(binary)):
           D.write(str(binary[i])+'\n')      

    with open (binaryfile,'r') as C: ###### PC COUNTER
       linesofbinary=C.readlines()
       with open(pcfile,'w') as D:
          PC = (len(linesofbinary)-1)*4
          D.write(str(PC))
          
  

print("""
##################################################################
@@       @@   @@@@  @@    @@  @@@@@@   @@   @@@@@@@    @@    @@
@@ @   @ @@   @  @  @@ @  @@  @    @   @@   @@   @@    @@    @@
@@   @   @@   @  @  @@  @ @@  @@@@@@   @@   @@@@@@        @@
@@       @@   @@@@  @@    @@  @    @   @@   @@    @@      @@
##################################################################

MIPS ASSEMBLER
All Rights Reserved to @AhmedElmonairy
-------------------------------------------------------------------------------------------------------
""")

print ('Reading File of Assembly')
print ('Converting to Machine Code..... \n')

main()
