import struct as st
def estereo2mono (ficEste, ficMono, canal=2):
    """
    La función lee el fichero `ficEste`, que debe contener una señal estéreo, 
    y escribe el fichero `ficMono`, con una señal monofónica. 
    El tipo concreto de señal que se almacenará en `ficMono` depende del argumento `canal`:

- `canal=0`: Se almacena el canal izquierdo $L$.
- `canal=1`: Se almacena el canal derecho $R$.
- `canal=2`: Se almacena la semisuma $(L+R)/2$. Es la opción por defecto.
- `canal=3`: Se almacena la semidiferencia $(L-R)/2$.

    """

    with open(ficEste, 'rb') as ficEn:
        cabecera = '<4sI4s'  
        buffer = ficEn.read(st.calcsize(cabecera))
        chunkID, chunksize, formatt = st.unpack(cabecera, buffer)

        formato = '<4sI2H2I2H'         
        buffer = ficEn.read(st.calcsize(formato)) 
        (subChunkID, subChunkSize, audioFormat,numChannels, sampleRate, byteRate,blockAlign, BitsxSample) = st.unpack(formato, buffer)

        cabecera = '<4sI'         
        buffer = ficEn.read(st.calcsize(cabecera))
        subChunk2ID, subChunk2Size = st.unpack(cabecera, buffer)

        numMuestrasmono = 2*subChunk2Size // blockAlign #dividimos por dos ya que en cada bloque nos interesa dividir los datos de cada canal
        datos = f'<{numMuestrasmono}h' 
        buffer = ficEn.read(st.calcsize(datos))
        Datos = st.unpack(datos, buffer)
    
        DatosL=Datos[0::4]
        DatosR=Datos[1::4]
        semisuma= [(dl+dr)//2 for  dl,dr in zip(DatosL,DatosR)]
        semiresta= [(dl-dr)//2 for dl,dr in zip(DatosL,DatosR)]
        
        #damos valores para crear cabecera nuevo archivo:
        bitsPerSampleM = 16
        sampleRateM = 16000
        numChannelsM = 1
        subChunk2sizeM = numMuestrasmono * numChannelsM * (bitsPerSampleM//8) //2
        chunkSizeM = 36 + subChunk2sizeM
        byteRateM = sampleRateM * numChannelsM * bitsPerSampleM//8
        blockAlignM = numChannelsM * bitsPerSampleM//8



        cabeceraOut = st.pack('4sI4s4sIhhIIhh4sI', chunkID, chunkSizeM, formatt, subChunkID, subChunkSize,
                            audioFormat, numChannelsM, sampleRateM, byteRateM, blockAlignM , bitsPerSampleM, subChunk2ID, subChunk2sizeM)
        with open(ficMono, 'wb') as Fsal:
            Fsal.write(cabeceraOut)
            if canal == 0:
                binario = st.pack(f'{len(DatosL)}i', *DatosL)
                Fsal.write(binario)
            if canal == 1:
                binario = st.pack(f'{len(DatosR)}i', *DatosR)
                Fsal.write(binario)
            if canal == 2:
                binario = st.pack(f'{len(semisuma)}i', *semisuma)
                Fsal.write(binario)
            if canal == 3:
                binario = st.pack(f'{len(semiresta)}i', *semiresta)
                Fsal.write(binario)

def mono2estereo(ficIzq, ficDer, ficEste):
    """
    Lee los ficheros ficIzq y ficDer, que contienen las señales monofónicas correspondientes
    a los canales izquierdo y derecho, respectivamente, y construye con ellas una señal estéreo 
    que almacena en el fichero ficEste.

    """
    #extraemos datos dicIzq
    with open(ficIzq, 'rb') as izq:
        cabecera = '<4sI4s'  
        buffer = izq.read(st.calcsize(cabecera))
        chunkID, chunksize, formatt = st.unpack(cabecera, buffer)

        formato = '<4sI2H2I2H'         
        buffer = izq.read(st.calcsize(formato)) 
        (subChunkID, subChunkSize, audioFormat,numChannels, sampleRate, byteRate,blockAlign, BitsxSample) = st.unpack(formato, buffer)

        cabecera = '<4sI'         
        buffer = izq.read(st.calcsize(cabecera))
        subChunk2ID, subChunk2Size = st.unpack(cabecera, buffer)

        numMuestras = 8*subChunk2Size//16
        datosl = f'<{numMuestras}h' 
        buffer = izq.read(st.calcsize(datosl))
        DatosL = st.unpack(datosl, buffer)
        
    #extraemos datos dicDer
    with open(ficDer, 'rb') as der:
        cabecera = '<4sI4s'  
        buffer = der.read(st.calcsize(cabecera))
        chunkID, chunksize, formatt = st.unpack(cabecera, buffer)

        formato = '<4sI2H2I2H'         
        buffer = der.read(st.calcsize(formato)) 
        (subChunkID, subChunkSize, audioFormat,numChannels, sampleRate, byteRate,blockAlign, BitsxSample) = st.unpack(formato, buffer)

        cabecera = '<4sI'         
        buffer = der.read(st.calcsize(cabecera))
        subChunk2ID, subChunk2Size = st.unpack(cabecera, buffer)

        numMuestras =  8*subChunk2Size//16 
        datosr = f'<{numMuestras}h' 
        buffer = der.read(st.calcsize(datos))
        DatosR = st.unpack(datosr, buffer)
    
    #damos valores para crear cabecera nuevo archivo:
        bitsPerSampleE = 16
        sampleRateE = 16000
        numChannelsE = 2
        subChunk2sizeE = numMuestras * numChannelsE * (bitsPerSampleE//8)
        chunkSizeE = 36 + subChunk2sizeE
        byteRateE = sampleRateE * numChannelsE * bitsPerSampleE//8
        blockAlignE = numChannelsE * bitsPerSampleE//8
    #Creamos la cabecera
    cabeceraOut = st.pack('4sI4s4sIhhIIhh4sI', chunkID, chunkSizeE, formatt, subChunkID, subChunkSize,
                            audioFormat, numChannelsE, sampleRateE, byteRateE, blockAlignE , bitsPerSampleE, subChunk2ID, subChunk2sizeE)
    #creamos la cadena de bits que contiene los datos L+R
    bitesout = bytearray()
    for i in range(len(DatosR)):
        bitesout.extend(st.pack('h', DatosL[i]))
        bitesout.extend(st.pack('h', DatosR[i]))
    
    with open(ficEste, 'wb') as Fsal:
            Fsal.write(cabeceraOut)
            Fsal.write(bitesout)



def codEstereo(ficEste, ficCod):
    """
    Lee el fichero \python{ficEste}, que contiene una señal estéreo codificada con PCM 
    lineal de 16 bits, y construye con ellas una señal codificada con 32 bits que permita 
    su reproducción tanto por sistemas monofónicos como por sistemas
    estéreo preparados para ello.

    """
    
    with open(ficEste, 'rb') as ficEn:
        cabecera = '<4sI4s'  
        buffer = ficEn.read(st.calcsize(cabecera))
        chunkIDin, chunksizein, formattin = st.unpack(cabecera, buffer)

        formato = '<4sI2H2I2H'         
        buffer = ficEn.read(st.calcsize(formato)) 
        (subChunkIDin, subChunkSizein, audioFormatin,numChannelsin, sampleRatein, byteRatein,blockAlignin, BitsxSamplein) = st.unpack(formato, buffer)

        cabecera = '<4sI'         
        buffer = ficEn.read(st.calcsize(cabecera))
        subChunk2IDin, subChunk2Sizein = st.unpack(cabecera, buffer)

        numMuestrasin = subChunk2Sizein // blockAlignin
        datos = f'<{numMuestrasin*2}h' 
        buffer = ficEn.read(st.calcsize(datos))
        Datos = st.unpack(datos, buffer)
    print('Longitud datos=')
    print(len(Datos))
   
   
    bitesout = bytearray()
    for i in range(0,len(Datos)-1,2):
        suma = (Datos[i] + Datos[i+1])//2
        resta = (Datos[i] - Datos[i+1])//2
        bitesout.extend(st.pack('<hh', suma, resta))
        
    print('Longitud salida=')
    print(len(bitesout))
    #damos valores para crear cabecera nuevo archivo:
    numeroMuestras = len(bitesout)
    bitsPerSampleC = 16
    subChunk1SizeC = 16
    sampleRateC = 16000
    numChannelsC = 2
    subChunk2sizeC = (numeroMuestras * numChannelsC * (bitsPerSampleC//8))
    chunkSizeC = 4 + (8 + subChunk1SizeC) + (8 + subChunk2sizeC)
    byteRateC = sampleRateC * numChannelsC * bitsPerSampleC//8
    blockAlignC = numChannelsC * bitsPerSampleC//8

    cabeceraOut = st.pack('4sI4s4sIHHIIHH4sI', chunkIDin, chunkSizeC, formattin, subChunkIDin, subChunkSizein,
                            audioFormatin, numChannelsC, sampleRateC, byteRateC, blockAlignC , bitsPerSampleC, subChunk2IDin, subChunk2sizeC)

    with open(ficCod, 'wb') as Fsal:
            Fsal.write(cabeceraOut)
            Fsal.write(bitesout)


def decEstereo(ficCod, ficDec):
    """
    Lee el fichero \python{ficCod} con una señal monofónica de 32 bits en la que
    los 16 bits más significativos contienen la semisuma de los dos canales de una señal estéreo
    y los 16 bits menos significativos la semidiferencia, y escribe el fichero \python{ficEste} 
    con los dos canales por separado en el formato de los ficheros WAVE estéreo.
    """

    with open(ficCod, 'rb') as ficEn:
        cabecera = '<4sI4s'  
        buffer = ficEn.read(st.calcsize(cabecera))
        chunkIDin, chunksizein, formattin = st.unpack(cabecera, buffer)

        formato = '<4sI2H2I2H'         
        buffer = ficEn.read(st.calcsize(formato)) 
        (subChunkIDin, subChunkSizein, audioFormatin,numChannelsin, sampleRatein, byteRatein,blockAlignin, BitsxSamplein) = st.unpack(formato, buffer)

        cabecera = '<4sI'         
        buffer = ficEn.read(st.calcsize(cabecera))
        subChunk2IDin, subChunk2Sizein = st.unpack(cabecera, buffer)

        numMuestrasin = subChunk2Sizein // blockAlignin
        datos = f'<{numMuestrasin}i' 
        bufferx = ficEn.read(st.calcsize(datos))
        print(len(bufferx))
        Datos = st.unpack(datos, bufferx)
    print('Longitud datos=')
    print(len(Datos))
    bitesout = bytearray()
    for i in Datos:
        suma = Datos[i]
        resta = Datos[i+1]
        L = suma + resta
        R = resta - suma
        bitesout.extend(st.pack('>h', L))
        bitesout.extend(st.pack('>h', R))
    numeroMuestras = len(bitesout)
    bitsPerSampleC = 16
    subChunk1SizeC = 16
    sampleRateC = 16000
    numChannelsC = 2
    subChunk2sizeC = (numeroMuestras * numChannelsC * (bitsPerSampleC//8))
    chunkSizeC = 4 + (8 + subChunk1SizeC) + (8 + subChunk2sizeC)
    byteRateC = sampleRateC * numChannelsC * bitsPerSampleC//8
    blockAlignC = numChannelsC * bitsPerSampleC//8

    cabeceraOut = st.pack('4sI4s4sIhhIIhh4sI', chunkIDin, chunkSizeC, formattin, subChunkIDin, subChunkSizein,
                            audioFormatin, numChannelsC, sampleRateC, byteRateC, blockAlignC , bitsPerSampleC, subChunk2IDin, subChunk2sizeC)

    with open(ficDec, 'wb') as Fsal:
            Fsal.write(cabeceraOut)
            Fsal.write(bitesout)






    

            
        
        




        

    
