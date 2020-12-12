responses = {
    "200": {
        "description": "Successful execution of request.",
        "headers": {
            "AF-TrackingId": {
                "type": "string"
            },
            "AF-SystemId": {
                "description": "Unique identifier for the responding system.",
                "type": "string"
            },
            "AF-ResponseTime": {
                "description": "The time it took for the system to process the request in milliseconds.",
                "type": "integer"
            },
            "AF-Confidentiality": {
                "description": "The level of confidentiality the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Correctness": {
                "description": "The level of correctness the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Availability": {
                "description": "The level of availability the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Traceability": {
                "description": "The level of traceability the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-EndUserId": {
                "x-amf-required": False,
                "description": "Identifies the calling enduser as authenticated by the calling system. Should only be used for tracing not authorization.",
                "type": "string"
            }
        },
        "x-amf-mediaType": "application/json",
        "schema": {
            "example": {
                "message": "Successful delete"
            }
        }
    },
    "403": {
        "description": "Forbidden",
        "x-amf-mediaType": "application/json",
        "schema": {
            "$ref": "#/definitions/ipfSimpleError"
        }
    },
    "400": {
        "description": "Bad Request",
        "headers": {
            "AF-TrackingId": {
                "type": "string"
            },
            "AF-SystemId": {
                "description": "Unique identifier for the responding system.",
                "type": "string"
            },
            "AF-ResponseTime": {
                "description": "The time it took for the system to process the request in milliseconds.",
                "type": "integer"
            },
            "AF-Confidentiality": {
                "description": "The level of confidentiality the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Correctness": {
                "description": "The level of correctness the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Availability": {
                "description": "The level of availability the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Traceability": {
                "description": "The level of traceability the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-EndUserId": {
                "x-amf-required": False,
                "description": "Identifies the calling enduser as authenticated by the calling system. Should only be used for tracing not authorization.",
                "type": "string"
            }
        },
        "x-amf-mediaType": "application/json",
        "schema": {
            "$ref": "#/definitions/ipfBaseError"
        }
    },
    "404": {
        "description": "Not Found",
        "headers": {
            "AF-TrackingId": {
                "type": "string"
            },
            "AF-SystemId": {
                "description": "Unique identifier for the responding system.",
                "type": "string"
            },
            "AF-ResponseTime": {
                "description": "The time it took for the system to process the request in milliseconds.",
                "type": "integer"
            },
            "AF-Confidentiality": {
                "description": "The level of confidentiality the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Correctness": {
                "description": "The level of correctness the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Availability": {
                "description": "The level of availability the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Traceability": {
                "description": "The level of traceability the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-EndUserId": {
                "x-amf-required": False,
                "description": "Identifies the calling enduser as authenticated by the calling system. Should only be used for tracing not authorization.",
                "type": "string"
            }
        },
        "x-amf-mediaType": "application/json",
        "schema": {
            "$ref": "#/definitions/ipfBaseError"
        }
    },
    "500": {
        "description": "Internal Server Error",
        "headers": {
            "AF-TrackingId": {
                "type": "string"
            },
            "AF-SystemId": {
                "description": "Unique identifier for the responding system.",
                "type": "string"
            },
            "AF-ResponseTime": {
                "description": "The time it took for the system to process the request in milliseconds.",
                "type": "integer"
            },
            "AF-Confidentiality": {
                "description": "The level of confidentiality the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Correctness": {
                "description": "The level of correctness the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Availability": {
                "description": "The level of availability the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-Traceability": {
                "description": "The level of traceability the responding system requires the data to be handled with.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            },
            "AF-EndUserId": {
                "x-amf-required": False,
                "description": "Identifies the calling enduser as authenticated by the calling system. Should only be used for tracing not authorization.",
                "type": "string"
            }
        },
        "x-amf-mediaType": "application/json",
        "schema": {
            "$ref": "#/definitions/ipfBaseError"
        }
    }
}
