# PowerShell script to create a simple icon for Hybrid Memory
# This creates a basic brain/memory themed icon

Add-Type -AssemblyName System.Drawing

# Create a 32x32 bitmap
$bitmap = New-Object System.Drawing.Bitmap(32, 32)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)

# Set background to transparent
$graphics.Clear([System.Drawing.Color]::Transparent)

# Define colors
$brainColor = [System.Drawing.Color]::FromArgb(100, 149, 237)  # Cornflower Blue
$neuronColor = [System.Drawing.Color]::FromArgb(255, 215, 0)   # Gold
$connectionColor = [System.Drawing.Color]::FromArgb(50, 205, 50) # Lime Green

# Draw brain outline (circle)
$brainBrush = New-Object System.Drawing.SolidBrush($brainColor)
$graphics.FillEllipse($brainBrush, 4, 4, 24, 24)

# Draw neural network nodes
$neuronBrush = New-Object System.Drawing.SolidBrush($neuronColor)
$graphics.FillEllipse($neuronBrush, 8, 8, 4, 4)
$graphics.FillEllipse($neuronBrush, 20, 8, 4, 4)
$graphics.FillEllipse($neuronBrush, 14, 16, 4, 4)
$graphics.FillEllipse($neuronBrush, 8, 20, 4, 4)
$graphics.FillEllipse($neuronBrush, 20, 20, 4, 4)

# Draw connections
$connectionPen = New-Object System.Drawing.Pen($connectionColor, 2)
$graphics.DrawLine($connectionPen, 10, 10, 22, 10)
$graphics.DrawLine($connectionPen, 16, 18, 10, 22)
$graphics.DrawLine($connectionPen, 16, 18, 22, 22)
$graphics.DrawLine($connectionPen, 10, 10, 16, 18)
$graphics.DrawLine($connectionPen, 22, 10, 16, 18)

# Clean up graphics
$graphics.Dispose()

# Save as ICO file
$iconPath = Join-Path $PSScriptRoot "hybrid_memory_icon.ico"

# Convert bitmap to icon
$iconStream = New-Object System.IO.MemoryStream
$bitmap.Save($iconStream, [System.Drawing.Imaging.ImageFormat]::Png)
$iconData = $iconStream.ToArray()

# Create ICO file header and write icon
$icoHeader = [byte[]](0, 0, 1, 0, 1, 0, 32, 32, 0, 0, 1, 0, 32, 0)
$icoHeader += [System.BitConverter]::GetBytes([int32]($iconData.Length + 22))
$icoHeader += [byte[]](22, 0, 0, 0)

[System.IO.File]::WriteAllBytes($iconPath, $icoHeader + $iconData)

Write-Host "Icon created: $iconPath"

# Clean up
$bitmap.Dispose()
$iconStream.Dispose()
$brainBrush.Dispose()
$neuronBrush.Dispose()
$connectionPen.Dispose()
