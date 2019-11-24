String := 1
OutVar := ""
StringTrimLeft, OutVar, String, 1

WinMaximize, Zemax OpticStudio
sleep, 700
WinActivate, Zemax OpticStudio
sleep, 700
WinSet, Top
sleep, 700

Send ^s
sleep, 500

Send ^+T ; Ctrl + Shift + T
sleep, 1000

send `t ;Tab
sleep, 50
send `t ;Tab
sleep, 50
Send {NumpadAdd}
sleep, 50
send `t ;Tab
sleep, 50
Send {NumpadAdd}
sleep, 50
send `t ;Tab
sleep, 50
Send {NumpadAdd}
sleep, 50
send `t ;Tab
sleep, 50
Send {NumpadAdd}
sleep, 50
send `t ;Tab

send ^a ;Ctrl + a
send `b ;Backspace
send {raw}%1%

send `t ;Tab
send `t ;Tab
Send `n ;Enter
sleep, 50
Send `n ;Enter


