from capstone import *
from capstone.riscv import *

def hex_to_riscv(hex_list, base_addr=0x80000000):
    # Criando o disassembler do Capstone para RISC-V
    md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32)
    md.detail = True

    # Convertendo a lista de hex em bytes
    code_bytes = b''.join(int(instr, 16).to_bytes(4, byteorder='little') for instr in hex_list)

    # Desmontando as instruções
    result = []
    for i, instr in enumerate(md.disasm(code_bytes, base_addr)):
        line = f"{instr.mnemonic} {instr.op_str}".strip()
        result.append(line)
    return result

# Exemplo de uso:
hex_instructions = [
    "0280006f",
    "41ee8e33",
    "007372b3",
    "0002a403",
    "008402b3",
    "fe5e08e3",
    "405f0eb3",
    "00092483",
    "064a0993",
    "000080e7",
    "fddff0ef"
]

assembly = hex_to_riscv(hex_instructions)

# Imprimir como arquivo .s para RARS
print(".text")
for line in assembly:
    print(f"    {line}")
