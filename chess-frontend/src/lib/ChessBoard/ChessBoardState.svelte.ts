type Space = {
    row: number;
    col: string;
    piece: Piece;
    color: "white" | "black" | "empty";
}

type Piece = {
    type: "empty" | "pawn" | "knight" | "bishop" | "rook" | "queen" | "king";
    color: "white" | "black" | "empty";
}

export class ChessBoardState {
    board: Space[][] = $state(this.generateBoard());
    constructor() {
        this.resetBoard();
        // $inspect(JSON.stringify(this.board));
    }
    
    generateBoard(): Space[][] {
        let gameBoard: Space[][] = [];
        let counter = 0;
        for(let i = 0; i < 8; i++) {
            gameBoard[i] = [];
            for(let j = 0; j < 8; j++) {
                const spot: Space = {
                    col: String.fromCharCode(97 + j),
                    row: (8-i),
                    piece: {
                        type: "empty",
                        color: "white"
                    },
                    color: (counter % 2 == 0 ? "white" : "black")
                }
                gameBoard[i].push(spot);
                counter++;
            }
            counter++;
        }
        return gameBoard;
    }

    getImageFromPiece(piece: Piece): string {
        if(piece.color == "white") {
            switch(piece.type) {
                case "pawn":
                    return "/pw.svg";
                case "knight":
                    return "/nw.svg";
                case "bishop":
                    return "/bw.svg";
                case "rook":
                    return "/rw.svg";
                case "queen":
                    return "/qw.svg";
                case "king":
                    return "/kw.svg";
                default:
                    return "/empty.svg";
            }
        }else if(piece.color == "black") {
            switch(piece.type) {
                case "pawn":
                    return "/pb.svg";
                case "knight":
                    return "/nb.svg";
                case "bishop":
                    return "/bb.svg";
                case "rook":
                    return "/rb.svg";
                case "queen":
                    return "/qb.svg";
                case "king":
                    return "/kb.svg";
                default:
                    return "/empty.svg";
            }
        }
        return "/empty.svg";
    }

    resetBoard() {
        this.board = this.generateBoard();
        this.board[0][0].piece.color = "black";
        this.board[0][0].piece.type = "rook";

        this.board[0][1].piece.color = "black";
        this.board[0][1].piece.type = "knight";
        
        this.board[0][2].piece.color = "black";
        this.board[0][2].piece.type = "bishop";

        this.board[0][3].piece.color = "black";
        this.board[0][3].piece.type = "queen";

        this.board[0][4].piece.color = "black";
        this.board[0][4].piece.type = "king";

        this.board[0][5].piece.color = "black";
        this.board[0][5].piece.type = "bishop";

        this.board[0][6].piece.color = "black";
        this.board[0][6].piece.type = "knight";

        this.board[0][7].piece.color = "black";
        this.board[0][7].piece.type = "rook";

        for(let i = 0; i < 8; i++) {
            this.board[1][i].piece.color = "black";
            this.board[1][i].piece.type = "pawn";
            
            this.board[2][i].piece.color = "empty";
            this.board[2][i].piece.type = "empty";

            this.board[3][i].piece.color = "empty";
            this.board[3][i].piece.type = "empty";

            this.board[4][i].piece.color = "empty";
            this.board[4][i].piece.type = "empty";

            this.board[5][i].piece.color = "empty";
            this.board[5][i].piece.type = "empty";

            this.board[6][i].piece.color = "white";
            this.board[6][i].piece.type = "pawn";
        }


        this.board[7][0].piece.color = "white";
        this.board[7][0].piece.type = "rook";

        this.board[7][1].piece.color = "white";
        this.board[7][1].piece.type = "knight";
        
        this.board[7][2].piece.color = "white";
        this.board[7][2].piece.type = "bishop";

        this.board[7][3].piece.color = "white";
        this.board[7][3].piece.type = "queen";

        this.board[7][4].piece.color = "white";
        this.board[7][4].piece.type = "king";

        this.board[7][5].piece.color = "white";
        this.board[7][5].piece.type = "bishop";

        this.board[7][6].piece.color = "white";
        this.board[7][6].piece.type = "knight";

        this.board[7][7].piece.color = "white";
        this.board[7][7].piece.type = "rook";
    }

    colToNum(col: string): number {
        return col.charCodeAt(0) - 97;
    }

    colToChar(col: number): string {
        return String.fromCharCode(col + 97);
    }

    movePiece(fromRowCol: string, toRowCol: string) {
        // format a1 (row 7 col a)
        console.log(8- (fromRowCol.charCodeAt(1) - '0'.charCodeAt(0)));
        let from: Space = this.getSpaceFromCordinate(fromRowCol); 
        let to: Space = this.getSpaceFromCordinate(toRowCol);
        console.log(JSON.stringify(from));
        console.log(JSON.stringify(to));
        if(from.piece.type == "empty") {
            console.log("Piece is empty");
            return;
        }
        // if(toRow < 0 || toRow > 7 || toCol.length != 1 || toCol < "a" || toCol > "h") {
        //     console.log("Invalid move");
        //     return;
        // }
        // if the space is empty then just replace

        if(this.board[to.row][this.colToNum(to.col)].piece.type == "empty") {
            // New Space
            console.log("adding to " + to.row + " " + this.colToNum(to.col));
            this.board[8-to.row][this.colToNum(to.col)].piece.color = from.piece.color;
            this.board[8-to.row][this.colToNum(to.col)].piece.type = from.piece.type;

            // Old Space
            console.log("removing from " + from.row + " " + this.colToNum(from.col));
            this.board[8-from.row][this.colToNum(from.col)].piece.color = "empty";
            this.board[8-from.row][this.colToNum(from.col)].piece.type = "empty";
        }
        this.board = this.board;
        
    }

    getSpace(row: number, col: string | number): Space {
        if(typeof col == "string") {
            col = this.colToNum(col);
        }else if(typeof col == "number") {
            col = col;
        }
        return this.board[row][col];
    }

    getSpaceFromCordinate(position: string): Space {
        
        const space = this.board[8-(position.charCodeAt(1) - '0'.charCodeAt(0))][position.charCodeAt(0) - 'a'.charCodeAt(0)];
        console.log(JSON.stringify(space));
        return space;
    }

    redrawBoard() {
        this.board = this.board;
    }

    pieceToFen(piece: Piece): string {
        if(piece.color == "white") {
            switch(piece.type) {
                case "pawn":
                    return "P";
                case "knight":
                    return "N";
                case "bishop":
                    return "B";
                case "rook":
                    return "R";
                case "queen":
                    return "Q";
                case "king":
                    return "K";
                default:
                    return "E";
            }
        }else if(piece.color == "black") {
            switch(piece.type) {
                case "pawn":
                    return "p";
                case "knight":
                    return "n";
                case "bishop":
                    return "b";
                case "rook":
                    return "r";
                case "queen":
                    return "q";
                case "king":
                    return "k";
                default:
                    return "e";
            }
        }
        return "?";
    }

    getFen() : string {
        let fen = "";
        let counter = 0;
        for(let i = 0; i < 8; i++) {
            for(let j = 0; j < 8; j++) {
                if(this.board[i][j].piece.type == "empty") {
                    counter++;
                    continue;
                }
                // not empty anymore so add the counter
                if(counter > 0 || counter == 8) {
                    fen += counter;
                    counter = 0;
                }
                fen += this.pieceToFen(this.board[i][j].piece);
            }
            if(counter > 0) {
                fen += counter;
                counter = 0;
            }
            fen += "/";
        }

        return fen;
    }
}