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

def dataHazardIdentifier(instructions, forwarding=False, insertNops=False, returnModifiedList=False):
    dataHazards = []
    modifiedInstructions = []
    previousRd = None
    previousOpcode = None

    i = 0
    while i < len(instructions):
        instruction = instructions[i]
        instr_type, binInstruction = classifyInstruction(instruction)
        opcode = binInstruction[25:]
        rd, rs1, rs2 = extractRegisters(instr_type, binInstruction)
        rdName, rs1Name, rs2Name = identifyRegisters(rd, rs1, rs2)

        conflictDetected = False

        if previousRd:
            if not forwarding:
                if rs1Name == previousRd or rs2Name == previousRd:
                    conflictDetected = True
            else:
                if previousOpcode == "0000011":  # LOAD
                    if rs1Name == previousRd or rs2Name == previousRd:
                        conflictDetected = True

        if conflictDetected:
            dataHazards.append((i, "RAW"))
            if insertNops:
                # Inserir NOP (hexadecimal: 00000013 → ADDI x0, x0, 0)
                nopInstruction = "00000013"
                modifiedInstructions.append(nopInstruction)
                print(f"NOP inserido antes da instrução {i+1} para evitar conflito (forwarding={'Sim' if forwarding else 'Não'})")

        modifiedInstructions.append(instruction)
        previousRd = rdName
        previousOpcode = opcode
        i += 1

    for hazard in dataHazards:
        num, tipo = hazard
        print(f"Conflito {tipo} detectado na instrução {num + 1}")

    if returnModifiedList:
        return modifiedInstructions
    return dataHazards


# CHAMADAS

def runAllAnalyses(instructions):
    print("Original:")
    for i, inst in enumerate(instructions, 1):
        print(f"Instrução {i}: {inst}")

    # 1 - Considerar que não foi implementada a técnica de forwarding e detectar a existência de conflito de dados.
    print("\n--- 1. Conflitos SEM forwarding (sem NOPs) ---")
    dataHazardIdentifier(instructions, forwarding=False, insertNops=False)

    # 2 - Considerar que não foi implementada a técnica de forwarding e detectar a existência de conflito de dados.
    print("\n--- 2. Conflitos COM forwarding (sem NOPs) ---")
    dataHazardIdentifier(instructions, forwarding=True, insertNops=False)

    # 3 - Considerar que não foi implementada a técnica de forwarding e incluir NOPS para evitar conflitos de dados.
    print("\n--- 3. Instruções COM NOPs (sem forwarding) ---")
    modifiedNoFw = dataHazardIdentifier(instructions, forwarding=False, insertNops=True, returnModifiedList=True)
    for i, inst in enumerate(modifiedNoFw, 1):
        print(f"Instrução {i}: {inst}")

    # 4 - Considerar que foi implementada a técnica de forwarding e incluir NOPS para evitar conflitos de dados.
    print("\n--- 4. Instruções COM NOPs (com forwarding) ---")
    modifiedFw = dataHazardIdentifier(instructions, forwarding=True, insertNops=True, returnModifiedList=True)
    for i, inst in enumerate(modifiedFw, 1):
        print(f"Instrução {i}: {inst}")


if __name__ == "__main__":
    archiveName = "original_dump"
    instructions = readHexFile(archiveName)

    runAllAnalyses(instructions)

    