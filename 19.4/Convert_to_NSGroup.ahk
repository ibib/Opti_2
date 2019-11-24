String := 1
OutVar := ""
StringTrimLeft, OutVar, String, 1

WinMaximize, Zemax OpticStudio
sleep, 700
WinActivate, Zemax OpticStudio
sleep, 700
WinSet, Top
sleep, 700

Send ^+T ; Ctrl + Shift + T
sleep, 1000

Loop 6 {
    send `t ;Tab
    sleep, 100
}

send ^a ;Ctrl + a
send `b ;Backspace
send {raw}%1%

Send `n ;Enter
sleep, 20
Send `n ;Enter
Send {NumpadAdd}
