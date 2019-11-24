String := 1
OutVar := ""
StringTrimLeft, OutVar, String, 1

WinMaximize, Zemax OpticStudio
sleep, 700
WinActivate, Zemax OpticStudio
sleep, 700
WinSet, Top
sleep, 700

Send ^+Y ; Ctrl + Shift + Y
sleep, 1000

;To spline segments
Loop 3 {
    send `t ;Tab
    sleep, 100
}

send 128 ;Select Spline segments
send `t ;Tab

;To Tolerance
Loop 3 {
    send `t ;Tab
    sleep, 100
}

send {End} ;Waehle letzte Toleranz

send `n ;Enter, bestaetigen der Konfiguaration
sleep, 100

;To Path
Loop 6 {
    send `t ;Tab
    sleep, 100
}

send {Space}
send {raw}%1%
send `n

;To Filename
Loop 6 {
    send `t ;Tab
    sleep, 100
}

send {raw}%2%
send `n ;Enter => Save

sleep, 20
send `n ;File already exists