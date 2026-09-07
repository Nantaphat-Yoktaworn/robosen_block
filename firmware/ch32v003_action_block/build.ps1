$gcc = "C:\Users\nnnn\AppData\Local\Arduino15\packages\esp32\tools\esp-rv32\2601\bin\riscv32-esp-elf-gcc.exe"
$objcopy = "C:\Users\nnnn\AppData\Local\Arduino15\packages\esp32\tools\esp-rv32\2601\bin\riscv32-esp-elf-objcopy.exe"
$currentDir = $PSScriptRoot

if (-not (Test-Path $gcc)) {
    Write-Error "GCC compiler not found at $gcc"
    exit 1
}

$params = @(
    "-march=rv32ec_zicsr",
    "-mabi=ilp32e",
    "-Os",
    "-flto",
    "-ffunction-sections",
    "-fdata-sections",
    "-Wl,--gc-sections",
    "-nostdlib",
    "-I$currentDir",
    "-T$currentDir\ch32fun.ld",
    "$currentDir\ch32fun.c",
    "$currentDir\main.c",
    "-o", "$currentDir\action_block.elf"
)

Write-Host "Compiling Action Block firmware for CH32V003..."
& $gcc $params

if ($LASTEXITCODE -eq 0) {
    & $objcopy -O binary "$currentDir\action_block.elf" "$currentDir\action_block.bin"
    $binSize = (Get-Item "$currentDir\action_block.bin").Length
    Write-Host "Build Successful! Output: $currentDir\action_block.bin ($binSize bytes)" -ForegroundColor Green
} else {
    Write-Error "Build Failed with exit code $LASTEXITCODE"
    exit 1
}
