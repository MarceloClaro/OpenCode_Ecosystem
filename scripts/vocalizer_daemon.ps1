Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$cmdFile = "C:\Users\marce\Documents\OpenCode_Ecosystem\.vocalizer_cmd"
$lastText = ""

while ($true) {
    if (Test-Path $cmdFile) {
        try {
            $cmd = Get-Content $cmdFile -Raw
            if ($cmd) {
                $cmd = $cmd.Trim()
                if ($cmd -eq "EXIT") {
                    $synth.SpeakAsyncCancelAll()
                    Remove-Item $cmdFile -Force
                    break
                }
                elseif ($cmd -eq "STOP") {
                    $synth.SpeakAsyncCancelAll()
                }
                elseif ($cmd -eq "PAUSE") {
                    $synth.Pause()
                }
                elseif ($cmd -eq "RESUME") {
                    $synth.Resume()
                }
                elseif ($cmd -eq "REPEAT") {
                    if ($lastText) {
                        $synth.SpeakAsyncCancelAll()
                        [void]$synth.SpeakAsync($lastText)
                    }
                }
                elseif ($cmd.StartsWith("PLAY:")) {
                    $text = $cmd.Substring(5).Trim()
                    if ($text) {
                        $lastText = $text
                        $synth.SpeakAsyncCancelAll()
                        [void]$synth.SpeakAsync($text)
                    }
                }
            }
            Remove-Item $cmdFile -Force
        }
        catch {
            # Evita erros se o arquivo estiver sendo gravado no mesmo instante
        }
    }
    Start-Sleep -Milliseconds 150
}
