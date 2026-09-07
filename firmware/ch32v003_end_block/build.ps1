$gcc = "C:\Users\nnnn\AppData\Local\Arduino15\packages\esp32\tools\esp-rv32\2601\bin\riscv32-esp-elf-gcc.exe"
$objcopy = "C:\Users\nnnn\AppData\Local\Arduino15\packages\esp32\tools\esp-rv32\2601\bin\riscv32-esp-elf-objcopy.exe"
$currentDir = $PSScriptRoot

if (-not (Test-Path $gcc)) {
    Write-Error "GCC compiler not found at $gcc"
    exit 1
}

# Preprocess linker script specifically for CH32V003 target (Target 0: 16K Flash, 2K RAM)
& $gcc -E -P -x c-header -DCH32V003=1 -DTARGET_MCU_LD=0 -I "$currentDir" "$currentDir\ch32fun.ld" -o "$currentDir\ch32fun_003.ld"

$params = @(
    "-march=rv32ec_zicsr",
    "-mabi=ilp32e",
    "-DCH32V003=1",
    "-Os",
    "-flto",
    "-ffunction-sections",
    "-fdata-sections",
    "-Wl,--gc-sections",
    "-nostdlib",
    "-I$currentDir",
    "-T$currentDir\ch32fun_003.ld",
    "$currentDir\ch32fun.c",
    "$currentDir\main.c",
    "-o", "$currentDir\end_block.elf"
)

Write-Host "Compiling Smart End Block firmware for CH32V003..."
& $gcc $params

if ($LASTEXITCODE -eq 0) {
    & $objcopy -O binary "$currentDir\end_block.elf" "$currentDir\end_block.bin"
    $binSize = (Get-Item "$currentDir\end_block.bin").Length
    Write-Host "Build Successful! Output: $currentDir\end_block.bin ($binSize bytes)" -ForegroundColor Green
} else {
    Write-Error "Build Failed with exit code $LASTEXITCODE"
    exit 1
}
