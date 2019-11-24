String := 1
OutVar := ""
StringTrimLeft, OutVar, String, 1

WinMaximize, Zemax OpticStudio
sleep, 700
WinActivate, Zemax OpticStudio
sleep, 700
WinSet, Top
sleep, 700

Send ^d ; Ctrl + d
sleep, 1000


;To clear_n_trace
Loop 7 {
    send `t ;Tab
    sleep, 100
}

send `t ;Tab
send {NumpadAdd}
send `t ;Tab
send {NumpadAdd}
send `t ;Tab
send {NumpadAdd}

send `n ;Enter, Start the tracing