def readHexFile(archiveName):
    with open(archiveName, "r") as file:
        instructions = file.readlines()
    return [line.strip() for line in instructions]

def convertHexToBin(instruction):
    binInstruction = bin(int(instruction, 16))[2:].zfill(32)
    return binInstruction

def classifyInstruction(instruction):
    binInstructions = (convertHexToBin)(instruction)

    opcode = binInstructions[25:]
    type = "Desconhecido "

    if opcode == '0110011':
        type = "R"
    elif opcode in ['0010011', '0000011', '1100111', '1110011']:
        type = "I"
    elif opcode == '0100011':
        type = "S"
    elif opcode == '1100011':
        type = "B"
    elif opcode in ['0110111', '0010111']:
        type = "U"
    elif opcode == '1101111':
        type = "J"

    return type, binInstructions

def extractRegisters(type, binInstruction):
    rd, rs1, rs2 = None, None, None

    if type == "R":
        rd = int(binInstruction[20:25], 2)
        rs1 = int(binInstruction[12:17], 2)
        rs2 = int(binInstruction[7:12], 2)
    if type == "I":
        rd = int(binInstruction[20:25], 2)
        rs1 = int(binInstruction[13:18], 2)
        rs2 = None
    if type == "S":
        rd = None
        rs1 = int(binInstruction[12:17], 2)
        rs2 = int(binInstruction[7:12], 2)
    if type == "B":
        rd = None
        rs1 = int(binInstruction[12:17], 2)
        rs2 = int(binInstruction[7:12], 2)
    if type == "U":
        rd = int(binInstruction[20:25], 2)
        rs1 = None
        rs2 = None
    if type == "J":
        rd = int(binInstruction[20:25], 2)
        rs1 = None
        rs2 = None
    return rd, rs1, rs2
        

def identifyRegisters(rd, rs1, rs2):
    registers  = { 
        0: "x0", 1: "x1", 2: "x2", 3: "x3", 4: "x4", 5: "x5", 6: "x6", 7: "x7", 8: "x8",
        9: "x9", 10: "x10", 11: "x11", 12: "x12", 13: "x13", 14: "x14", 15: "x15", 16: "x16",
        17: "x17", 18: "x18", 19: "x19", 20: "x20", 21: "x21", 22: "x22", 23: "x23", 24: "x24",
        25: "x25", 26: "x26", 27: "x27", 28: "x28", 29: "x29", 30: "x30", 31: "x31"
    } 

    rdName = registers.get(rd, "Unknown")
    rs1Name = registers.get(rs1, "Unknown")
    rs2Name = registers.get(rs2, "Unknown")
    return rdName, rs1Name, rs2Name

def dataHazardIdentifier(instructions):
    instructionNumber = -1
    dataHazards = []

    previousRd = None
    previousRs1 = None
    previousRs2 = None

    for instruction in instructions:
        instructionNumber += 1

        type, binInstruction = classifyInstruction(instruction)
        rd, rs1, rs2 = extractRegisters(type, binInstruction)
        rdName, rs1Name, rs2Name = identifyRegisters(rd, rs1, rs2)

        # RAW: instrução atual LÊ registrador escrito pela anterior
        if previousRd and (rs1Name == previousRd or rs2Name == previousRd):
            dataHazards.append((instructionNumber, "RAW"))

        # WAR: instrução atual ESCREVE registrador lido pela anterior
        if rdName and (previousRs1 == rdName or previousRs2 == rdName):
            dataHazards.append((instructionNumber, "WAR"))

        # WAW: instrução atual ESCREVE registrador já escrito pela anterior
        if rdName and previousRd and rdName == previousRd:
            dataHazards.append((instructionNumber, "WAW"))

        previousRd = rdName
        previousRs1 = rs1Name
        previousRs2 = rs2Name

    for hazard in dataHazards:
        num, tipo = hazard
        print(f"Conflito {tipo} detectado na instrução {num}")

    print(dataHazards)

    return dataHazards


# 1 - Considerar que não foi implementada a técnica de forwarding e detectar a existência de conflito de dados.
def notUsingForwarding(instructions):
    dataHazards = []
    previousRd = None
    instructionNumber = -1

    for instruction in instructions:
        instructionNumber += 1
        type, binInstruction = classifyInstruction(instruction)
        rd, rs1, rs2 = extractRegisters(type, binInstruction)
        rdName, rs1Name, rs2Name = identifyRegisters(rd, rs1, rs2)

        if previousRd and (rs1Name == previousRd or rs2Name == previousRd):
            dataHazards.append(instructionNumber)

        previousRd = rdName       

    if dataHazards:
        print(f"Conflito de dados detectado nas instruções: {dataHazards}")
    else:
        print("Nenhum conflito de dados detectado.")    

    return dataHazards


# 2 - Considerar que não foi implementada a técnica de forwarding e detectar a existência de conflito de dados.
def usingForwarding(instructions):
    previousRd = None
    previousOpcode = None
    dataHazards = []
    instructionNumber = -1


    for instruction in instructions:
        type, binInstruction = classifyInstruction(instruction)
        opcode = binInstruction[25:]
        rd, rs1, rs2 = extractRegisters(type, binInstruction)
        rdName, rs1Name, rs2Name = identifyRegisters(rd, rs1, rs2)

        if previousOpcode == "0000011": # Olhar para instrucoes de LOAD
              if rs1Name == previousRd or rs2Name == previousRd:
                  dataHazards.append(instructionNumber)

        previousOpcode = opcode
        previousRd = rdName

    if dataHazards:
        print(f"Conflito de dados detectado nas instruções: {dataHazards}")
    else:
        print("Nenhum conflito de dados detectado.")   
    return dataHazards

if __name__ == "__main__":
    archiveName = "ex1_dump_hazard"
    instructions = readHexFile(archiveName)

    print("Original:")
    for i in instructions:
        instructionNumber = instructions.index(i) + 1
        print (f"Instrução: {instructionNumber} {i}")
        

    print("\n--- Análise de Conflitos ---")
    dataHazardIdentifier(instructions)

    print("\n--- Análise de Conflitos (sem forwarding) ---")
    noFwList = notUsingForwarding(instructions)

    print("\n--- Análise de Conflitos (com forwarding) ---")
    fwList = usingForwarding(instructions)


    