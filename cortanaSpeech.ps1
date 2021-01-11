

# Windows 10 Text-to-Speech Example

Add-Type -AssemblyName System.Speech
$SpeechSynthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
$SpeechSynthesizer.SelectVoice("Microsoft Eva Mobile")
$SpeechSynthesizer.Rate = 0  # -10 is slowest, 10 is fastest

$WavFileOut = Join-Path -Path $env:USERPROFILE -ChildPath "Desktop\thinkpowershell-demo.wav"
$SpeechSynthesizer.SetOutputToWaveFile($WavFileOut)

$RecordedText = '
Thank you for trying out the Think PowerShell Text-to-speech demo.
Learn more at thinkpowershell.com.
'

$SpeechSynthesizer.Speak($RecordedText)
$SpeechSynthesizer.Dispose()
