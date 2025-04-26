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
    return rd, rs1, rs2

def identifyRegisters(rd, rs1, rs2):
    registers  = { #Validar para colocar o NOME do registrador, não o numero
        0: "x0", 1: "x1", 2: "x2", 3: "x3", 4: "x4", 5: "x5", 6: "x6", 7: "x7", 8: "x8",
        9: "x9", 10: "x10", 11: "x11", 12: "x12", 13: "x13", 14: "x14", 15: "x15", 16: "x16",
        17: "x17", 18: "x18", 19: "x19", 20: "x20", 21: "x21", 22: "x22", 23: "x23", 24: "x24",
        25: "x25", 26: "x26", 27: "x27", 28: "x28", 29: "x29", 30: "x30", 31: "x31"
    } 
    # Utilizar o REG, se for printar, mostrar o NOME.

    rdName = registers.get(rd, "Unknown")
    rs1Name = registers.get(rs1, "Unknown")
    rs2Name = registers.get(rs2, "Unknown") if rs2 is not None else "N/A"
    return rdName, rs1Name, rs2Name


if __name__ == "__main__":
    archiveName = "ex1_dump"
    instructions = readHexFile(archiveName)

    for instruction in instructions:
        type, binInstruction = classifyInstruction(instruction)
        rd, rs1, rs2 = extractRegisters(type, binInstruction)
        rdName, rs1Name, rs2Name = identifyRegisters(rd, rs1, rs2)

        print(f"Instruction: {instruction}, Type: {type}, Registers: rd: {rdName}, rs1: {rs1Name}, rs2 {rs2Name}")

    