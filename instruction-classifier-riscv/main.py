def readHexFile(archiveName):
    #Lê um arquivo de texto e retorna uma lista de instruções.
    with open(archiveName, "r") as file:
        instructions = file.readlines()
    return [line.strip() for line in instructions]

def processInstructions(instructions):
    count = {
        'R': 0,
        'I': 0,
        'S': 0,
        'B': 0,
        'U': 0,
        'J': 0,
        'Desconhecido' : 0
    }
    result = []

    for instruction in instructions:
        type = classifyInstruction(instruction)
        count[type] += 1
        result.append((instruction, type))

    return result, count

def classifyInstruction(hexInstruction):
    binInstruction = bin(int(hexInstruction, 16))[2:].zfill(32) #Hex para Bin, completando até 32bits

    opcode = binInstruction[25:] #Ultimos 7 bits
    type = "Desconhecido"

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

    return type

def printResult(result, count):
    for instruction, type in result:
        print(f"{instruction} -> Tipo: {type}")
    print("\nQuantidade por tipo:")
    for type, quantity in count.items():
        print(f"{type}: {quantity}")

if __name__ == "__main__":
    archiveName = "ex2_dump"
    instructions = readHexFile(archiveName)
    result, count = processInstructions(instructions)
    printResult(result, count)