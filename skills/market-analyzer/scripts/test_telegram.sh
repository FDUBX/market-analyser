#!/bin/bash
# Test Telegram notification

GATEWAY_URL="http://localhost:18789"
GATEWAY_TOKEN="d2a8e12b4171c491739729caaa55a94da04e19598b56686a"
TELEGRAM_USER="6812190723"

MESSAGE="🧪 Test de notification Market Analyzer

Ceci est un message de test pour vérifier que les alertes Telegram fonctionnent correctement.

✅ Si tu reçois ce message, le système d'alertes est opérationnel !

⏰ $(date '+%Y-%m-%d %H:%M:%S')
🔗 Dashboard: http://192.168.1.64:8080/live"

PAYLOAD=$(cat <<EOF
{
  "action": "send",
  "channel": "telegram",
  "target": "$TELEGRAM_USER",
  "message": $(echo "$MESSAGE" | jq -Rs .)
}
EOF
)

echo "📤 Envoi du message de test..."
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/message" \
    -H "Authorization: Bearer $GATEWAY_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Message envoyé avec succès !"
    echo ""
    echo "Vérifie ton Telegram, tu devrais avoir reçu le message de test."
else
    echo "❌ Échec de l'envoi (HTTP $HTTP_CODE)"
    echo ""
    echo "Réponse:"
    echo "$BODY"
fi
