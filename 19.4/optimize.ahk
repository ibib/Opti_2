String := 1
OutVar := ""
StringTrimLeft, OutVar, String, 1

WinMaximize, Zemax OpticStudio
sleep, 700
WinActivate, Zemax OpticStudio
sleep, 700
WinSet, Top
sleep, 700

Send ^+O ; Ctrl + Shift + O
sleep, 1000

send `t ;Tab
send `t ;Tab
send d ;D

send `t ;Tab
send `t ;Tab

send {End}
send {Up}
send {Up}

send `t ;Tab
send {NumpadAdd}
send `t ;Tab

send `n ;Enter
