# Tests Gitea API access and checks for GitHub mirrors on a repository
$tokenLine = Get-Content .env |
  Where-Object { $_ -match '^\s*GITEA_TOKEN\s*=' } |
  Select-Object -First 1

if (-not $tokenLine) { throw "GITEA_TOKEN was not found in .env" }

$env:GITEA_TOKEN = ($tokenLine -replace '^\s*GITEA_TOKEN\s*=\s*', '').Trim().Trim('"').Trim("'")
$api = "https://git.tirsystem.com/api/v1"
$repo = "Tirsvad-Udemy-100_days_of_code/001-band_name_generator"
$headers = @(
  "Authorization: token $env:GITEA_TOKEN",
  "Accept: application/json"
)

foreach ($path in @("/repos/$repo", "/repos/$repo/push_mirrors")) {
  $raw = (& curl.exe --silent --show-error --max-time 20 `
    --write-out "`n__HTTP_STATUS__%{http_code}" `
    --header $headers[0] --header $headers[1] "$api$path" | Out-String)

  $marker = "__HTTP_STATUS__"
  $index = $raw.LastIndexOf($marker)
  if ($index -lt 0) {
    Write-Output "No HTTP response for $path. curl exit code: $LASTEXITCODE"
    continue
  }

  $body = $raw.Substring(0, $index).TrimEnd("`r", "`n")
  $status = $raw.Substring($index + $marker.Length).Trim()
  Write-Output "$path -> HTTP $status"

  if ($status -eq "200" -and $path.EndsWith("/push_mirrors")) {
    $body | ConvertFrom-Json | ForEach-Object {
      $match = [regex]::Match(
        [string]$_.remote_address,
        'github\.com[:/](?<target>[^?#]+)'
      )
      if ($match.Success) {
        Write-Output ("GitHub mirror: github.com/{0}" -f ($match.Groups["target"].Value -replace '\.git$', ''))
      } else {
        Write-Output "Mirror found; GitHub target could not be identified."
      }
    }
  } elseif ($status -ne "200") {
    try {
      $errorBody = $body | ConvertFrom-Json
      if ($errorBody.message) { Write-Output $errorBody.message }
    } catch {}
  }
}

Remove-Item Env:\GITEA_TOKEN