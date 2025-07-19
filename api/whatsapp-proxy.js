// WhatsApp Business API 프록시
export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { message, to } = req.body;
        
        // WhatsApp Business API 호출
        const response = await fetch(
            `https://graph.facebook.com/v17.0/${process.env.WHATSAPP_PHONE_ID}/messages`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${process.env.WHATSAPP_TOKEN}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    messaging_product: 'whatsapp',
                    to: to,
                    type: 'text',
                    text: { body: message }
                })
            }
        );

        const data = await response.json();
        
        if (response.ok) {
            res.status(200).json({ success: true, data });
        } else {
            res.status(400).json({ success: false, error: data });
        }
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
}