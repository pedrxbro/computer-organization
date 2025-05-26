def readHexFile(archiveName):
    with open(archiveName, "r") as file:
        instructions = file.readlines()
    return [line.strip() for line in instructions]

def convertHexToBin(instruction):
    binInstruction = bin(int(instruction, 16))[2:].zfill(32)
    return binInstruction

def classifyInstruction(instruction):
    binInstructions = convertHexToBin(instruction)
    opcode = binInstructions[25:]
    type = "Desconhecido"

    if opcode == '0110011':
        type = "R"
    elif opcode in ['0010011', '0000011', '1100111', '1110011']:
        type = "I"
    elif opcode == '0100011':
        type = "S"
    elif opcode == '1100011':
        type = "B"  # Tipo de desvio condicional
    elif opcode in ['0110111', '0010111']:
        type = "U"
    elif opcode == '1101111':
        type = "J"  # Tipo de desvio incondicional

    return type, binInstructions

def extractRegisters(type, binInstruction):
    rd, rs1, rs2 = None, None, None

    if type == "R":
        rd = int(binInstruction[20:25], 2)
        rs1 = int(binInstruction[12:17], 2)
        rs2 = int(binInstruction[7:12], 2)
    elif type == "I":
        rd = int(binInstruction[20:25], 2)
        rs1 = int(binInstruction[12:17], 2)
    elif type == "S":
        rs1 = int(binInstruction[12:17], 2)
        rs2 = int(binInstruction[7:12], 2)
    elif type == "B":
        rs1 = int(binInstruction[12:17], 2)
        rs2 = int(binInstruction[7:12], 2)
    elif type == "U":
        rd = int(binInstruction[20:25], 2)
    elif type == "J":
        rd = int(binInstruction[20:25], 2)
    return rd, rs1, rs2

def identifyRegisters(rd, rs1, rs2):
    registers  = {i: f"x{i}" for i in range(32)}
    rdName = registers.get(rd, "Unknown")
    rs1Name = registers.get(rs1, "Unknown")
    rs2Name = registers.get(rs2, "Unknown")
    return rdName, rs1Name, rs2Name

def isControlInstruction(opcode):
    return opcode in ['1100011', '1101111']  # B-type (condicional) e J-type (jump)

def dataHazardIdentifier(instructions, forwarding=False, insertNops=False, reorder=False, returnModifiedList=False, controlHazards=False, delayedBranch=False):
    dataHazards = []
    modifiedInstructions = []
    i = 0

    while i < len(instructions):
        instruction = instructions[i]
        instr_type, binInstruction = classifyInstruction(instruction)
        opcode = binInstruction[25:]
        rd, rs1, rs2 = extractRegisters(instr_type, binInstruction)
        rdName, rs1Name, rs2Name = identifyRegisters(rd, rs1, rs2)

        conflictDetected = False

        # RAW data hazard
        if modifiedInstructions:
            prevInstr = modifiedInstructions[-1]
            prevType, prevBin = classifyInstruction(prevInstr)
            prevOpcode = prevBin[25:]
            prevRd, _, _ = extractRegisters(prevType, prevBin)
            prevRdName, _, _ = identifyRegisters(prevRd, None, None)

            if prevRdName:
                if not forwarding or (forwarding and prevOpcode == "0000011"):
                    if rs1Name == prevRdName or rs2Name == prevRdName:
                        conflictDetected = True

        if conflictDetected:
            dataHazards.append((i, "RAW"))
            if reorder:
                j = i + 1
                found = False
                while j < len(instructions):
                    nextInstr = instructions[j]
                    nextType, nextBin = classifyInstruction(nextInstr)
                    _, nextRs1, nextRs2 = extractRegisters(nextType, nextBin)
                    _, nextRs1Name, nextRs2Name = identifyRegisters(None, nextRs1, nextRs2)
                    if prevRdName not in [nextRs1Name, nextRs2Name]:
                        instructions[i], instructions[j] = instructions[j], instructions[i]
                        found = True
                        break
                    j += 1
                if found:
                    continue
            elif insertNops:
                modifiedInstructions.append("00000013")  # NOP
                print(f"NOP inserido antes da instrução {i+1} para evitar conflito de dados")

        modifiedInstructions.append(instruction)

        # Controle de desvios
        if controlHazards and isControlInstruction(opcode):
            modifiedInstructions.append("00000013")  # NOP
            print(f"NOP inserido após desvio na instrução {i+1} (controle de fluxo)")

        # Desvio retardado (delayed branch)
        elif delayedBranch and isControlInstruction(opcode):
            if i + 1 < len(instructions):
                useful = instructions[i + 1]
                modifiedInstructions.append(useful)
                print(f"Instrução útil movida após desvio (delayed branch): {useful}")
                i += 1 
            else:
                modifiedInstructions.append("00000013")
                print(f"NOP inserido após desvio (delayed branch)")

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

    print("\n--- 1. Conflitos SEM forwarding (sem NOPs) ---")
    dataHazardIdentifier(instructions)

    print("\n--- 2. Conflitos COM forwarding (sem NOPs) ---")
    dataHazardIdentifier(instructions, forwarding=True)

    print("\n--- 3. Instruções COM NOPs (sem forwarding) ---")
    modifiedNoFw = dataHazardIdentifier(instructions[:], forwarding=False, insertNops=True, returnModifiedList=True)
    for i, inst in enumerate(modifiedNoFw, 1):
        print(f"Instrução {i}: {inst}")

    print("\n--- 4. Instruções COM NOPs (com forwarding) ---")
    modifiedFw = dataHazardIdentifier(instructions[:], forwarding=True, insertNops=True, returnModifiedList=True)
    for i, inst in enumerate(modifiedFw, 1):
        print(f"Instrução {i}: {inst}")

    print("\n--- 5. Reordenação para reduzir NOPs (sem forwarding) ---")
    reorderedNoFw = dataHazardIdentifier(instructions[:], forwarding=False, insertNops=True, reorder=True, returnModifiedList=True)
    for i, inst in enumerate(reorderedNoFw, 1):
        print(f"Instrução {i}: {inst}")

    print("\n--- 6. Reordenação para reduzir NOPs (com forwarding) ---")
    reorderedFw = dataHazardIdentifier(instructions[:], forwarding=True, insertNops=True, reorder=True, returnModifiedList=True)
    for i, inst in enumerate(reorderedFw, 1):
        print(f"Instrução {i}: {inst}")

    print("\n--- 7. Inserção de NOPs para evitar conflitos de controle (desvios) ---")
    ctrlHazards = dataHazardIdentifier(instructions[:], controlHazards=True, returnModifiedList=True)
    for i, inst in enumerate(ctrlHazards, 1):
        print(f"Instrução {i}: {inst}")

    print("\n--- 8. Técnica de desvio retardado (delayed branch) ---")
    delayed = dataHazardIdentifier(instructions[:], delayedBranch=True, returnModifiedList=True)
    for i, inst in enumerate(delayed, 1):
        print(f"Instrução {i}: {inst}")

    print("\n--- 9. Combinação: NOPs + Reordenação (com forwarding) ---")
    combined = dataHazardIdentifier(instructions[:], forwarding=True, insertNops=True, reorder=True, returnModifiedList=True)
    for i, inst in enumerate(combined, 1):
        print(f"Instrução {i}: {inst}")


if __name__ == "__main__":
    archiveName = "original_dump"
    instructions = readHexFile(archiveName)
    runAllAnalyses(instructions)
